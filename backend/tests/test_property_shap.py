"""Property-based tests for SHAP validation detection logic.

**Validates: Requirements 7.2, 7.3**

Tests that the Phase 7 (SHAPValidationPhase) correctly validates:
- Property 9: SHAP Additivity — detection logic identifies code that validates
  the additivity property (sum of SHAP values + base_value ≈ prediction).
- Property 10: Explanation Response Completeness — detection logic correctly
  identifies whether explanation responses contain all required fields
  (feature_name, shap_value, direction).
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hypothesis import given, settings, assume
from hypothesis.strategies import (
    booleans,
    composite,
    floats,
    integers,
    just,
    lists,
    one_of,
    sampled_from,
    text,
    tuples,
)

from audit.phases.phase_07_shap import SHAPValidationPhase


# --------------------------------------------------------------------------
# Strategies for Property 9: SHAP Additivity
# --------------------------------------------------------------------------

# Patterns that the additivity detection looks for
ADDITIVITY_CODE_PATTERNS = [
    'base_value = explainer.expected_value',
    'expected_value = explainer.expected_value[0]',
    'assert np.isclose(sum(shap_values) + base_value, prediction)',
    'if abs(prediction - base_value - sum(shap_values)) > 0.01:',
    'additivity_check = sum(shap_values) + base_value',
    'np.isclose(shap_sum + base_value, prediction, atol=0.01)',
    'shap_values_sum = np.sum(shap_values)',
]

# Code snippets that should NOT trigger additivity detection
NON_ADDITIVITY_CODE = [
    'def predict(self, features):\n    return self.model.predict(features)',
    'class Explainer:\n    def explain(self, x):\n        return self.shap_explain(x)',
    'import numpy as np\n\ndef compute_features(df):\n    return df.values',
    'logger.info("Computing explanation")\nresult = model.predict(data)',
    'def get_feature_names(self):\n    return self._features',
]


@composite
def additivity_code_with_pattern(draw):
    """Generate Python code that contains SHAP additivity validation logic.

    Returns (source_code, True) since it should be detected.
    """
    pattern_line = draw(sampled_from(ADDITIVITY_CODE_PATTERNS))

    # Surround with realistic context
    prefix_lines = [
        "import numpy as np",
        "import shap",
        "",
        "",
        "class ShapExplainer:",
        '    """SHAP explanation service."""',
        "",
        "    def __init__(self, model):",
        "        self._model = model",
        "        self.explainer = shap.TreeExplainer(self._model)",
        "",
        "    def explain(self, features):",
        '        """Compute SHAP values for given features."""',
        "        shap_values = self.explainer.shap_values(features)",
    ]

    suffix_lines = [
        "        return shap_values",
    ]

    source = "\n".join(prefix_lines) + "\n        " + pattern_line + "\n" + "\n".join(suffix_lines) + "\n"
    return source, True


@composite
def additivity_code_without_pattern(draw):
    """Generate Python code that does NOT contain SHAP additivity validation.

    Returns (source_code, False) since it should NOT be detected.
    """
    code_body = draw(sampled_from(NON_ADDITIVITY_CODE))
    source = code_body + "\n"
    return source, False


@composite
def additivity_detection_input(draw):
    """Generate either code with or without additivity patterns."""
    has_pattern = draw(booleans())
    if has_pattern:
        return draw(additivity_code_with_pattern())
    else:
        return draw(additivity_code_without_pattern())


# --------------------------------------------------------------------------
# Strategies for Property 10: Explanation Response Completeness
# --------------------------------------------------------------------------

# The three required field categories
FEATURE_NAME_PATTERNS = [
    'feature_name: str',
    'feature_name = Column(String)',
    '"feature_name": feat.name',
    "feature_name=exp.feature_name",
    'self.feature_name = name',
]

SHAP_VALUE_PATTERNS = [
    'shap_value: float',
    'shap_value = Column(Float)',
    '"shap_value": float(sv)',
    "shap_value=float(exp.shap_value)",
    'self.shap_value = value',
]

DIRECTION_PATTERNS = [
    'direction: str',
    'direction = "positive" if sv > 0 else "negative"',
    '"direction": "increases_churn"',
    'increases_churn = shap_val > 0',
    'decreases_churn = shap_val < 0',
    '"positive_contribution" if val > 0 else "negative_contribution"',
]

# Code that has NONE of the required fields
UNRELATED_CODE_LINES = [
    'def compute(self, x):',
    '    return self.model.predict(x)',
    'class BaseService:',
    '    pass',
    'import logging',
    'logger = logging.getLogger(__name__)',
]


@composite
def explanation_response_code(draw):
    """Generate synthetic code with a configurable mix of explanation fields.

    Returns (source_code, has_feature_name, has_shap_value, has_direction).
    """
    has_feature_name = draw(booleans())
    has_shap_value = draw(booleans())
    has_direction = draw(booleans())

    lines = [
        "from pydantic import BaseModel",
        "from typing import Optional, List",
        "",
        "",
    ]

    if has_feature_name:
        feature_line = draw(sampled_from(FEATURE_NAME_PATTERNS))
        lines.append(f"    {feature_line}")
        lines.append("")

    if has_shap_value:
        shap_line = draw(sampled_from(SHAP_VALUE_PATTERNS))
        lines.append(f"    {shap_line}")
        lines.append("")

    if has_direction:
        direction_line = draw(sampled_from(DIRECTION_PATTERNS))
        lines.append(f"    {direction_line}")
        lines.append("")

    # Add some filler if we have no fields (to avoid empty file)
    if not (has_feature_name or has_shap_value or has_direction):
        for line in UNRELATED_CODE_LINES:
            lines.append(line)

    source = "\n".join(lines) + "\n"
    return source, has_feature_name, has_shap_value, has_direction


# --------------------------------------------------------------------------
# Property 9: SHAP Additivity
# --------------------------------------------------------------------------


class TestSHAPAdditivity:
    """Property 9: SHAP Additivity.

    **Validates: Requirements 7.2**

    For any valid feature input passed to the SHAP explainer, the sum of all
    SHAP values plus the expected base value SHALL equal the model's raw
    prediction output (within floating-point tolerance of ±0.01).

    We test that the detection logic in SHAPValidationPhase correctly
    identifies code that validates (or does not validate) the additivity
    property.
    """

    @given(data=additivity_code_with_pattern())
    @settings(max_examples=100)
    def test_code_with_additivity_patterns_is_detected(self, data):
        """Code containing additivity validation patterns SHALL be detected.

        **Validates: Requirements 7.2**
        """
        source, expected_detection = data

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ml_dir = tmpdir_path / "ml"
            ml_dir.mkdir()
            services_dir = tmpdir_path / "services"
            services_dir.mkdir()

            # Write source to the ML directory (where the phase looks)
            shap_file = ml_dir / "shap_explainer.py"
            shap_file.write_text(source, encoding="utf-8")

            phase = SHAPValidationPhase()
            result = phase._check_additivity_validation(ml_dir, services_dir)

        assert result is True, (
            f"Expected additivity validation to be detected, but it was not.\n"
            f"Source:\n{source}"
        )

    @given(data=additivity_code_without_pattern())
    @settings(max_examples=100)
    def test_code_without_additivity_patterns_is_not_detected(self, data):
        """Code lacking additivity patterns SHALL NOT be flagged as present.

        **Validates: Requirements 7.2**
        """
        source, expected_detection = data

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ml_dir = tmpdir_path / "ml"
            ml_dir.mkdir()
            services_dir = tmpdir_path / "services"
            services_dir.mkdir()

            # Write source to services dir
            code_file = services_dir / "predict_service.py"
            code_file.write_text(source, encoding="utf-8")

            phase = SHAPValidationPhase()
            result = phase._check_additivity_validation(ml_dir, services_dir)

        assert result is False, (
            f"Expected no additivity validation detected, but it was.\n"
            f"Source:\n{source}"
        )

    @given(data=additivity_detection_input())
    @settings(max_examples=150)
    def test_additivity_detection_is_consistent(self, data):
        """Detection result SHALL be consistent with pattern presence.

        **Validates: Requirements 7.2**
        """
        source, has_pattern = data

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ml_dir = tmpdir_path / "ml"
            ml_dir.mkdir()
            services_dir = tmpdir_path / "services"
            services_dir.mkdir()

            code_file = ml_dir / "explainer.py"
            code_file.write_text(source, encoding="utf-8")

            phase = SHAPValidationPhase()
            result = phase._check_additivity_validation(ml_dir, services_dir)

        assert result == has_pattern, (
            f"Expected detection={has_pattern}, got detection={result}.\n"
            f"Source:\n{source}"
        )


# --------------------------------------------------------------------------
# Property 10: Explanation Response Completeness
# --------------------------------------------------------------------------


class TestExplanationResponseCompleteness:
    """Property 10: Explanation Response Completeness.

    **Validates: Requirements 7.3**

    For any SHAP explanation response, every item in the explanation list
    SHALL contain a `feature_name` (string), `shap_value` (numeric), and
    a `direction` indicator (positive or negative contribution).

    We test that the detection logic correctly identifies whether the code
    structure includes all three required fields.
    """

    @given(data=explanation_response_code())
    @settings(max_examples=150)
    def test_completeness_detection_matches_field_presence(self, data):
        """Detection SHALL report complete only when all 3 fields are present.

        **Validates: Requirements 7.3**
        """
        source, has_feature_name, has_shap_value, has_direction = data
        expected_complete = has_feature_name and has_shap_value and has_direction

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ml_dir = tmpdir_path / "ml"
            ml_dir.mkdir()
            services_dir = tmpdir_path / "services"
            services_dir.mkdir()
            schemas_dir = tmpdir_path / "schemas"
            schemas_dir.mkdir()

            # Write to schemas (where the phase looks for structure)
            schema_file = schemas_dir / "explanations.py"
            schema_file.write_text(source, encoding="utf-8")

            phase = SHAPValidationPhase()
            result = phase._check_explanation_output_structure(
                ml_dir, services_dir, schemas_dir
            )

        assert result == expected_complete, (
            f"Expected completeness={expected_complete}, got={result}.\n"
            f"has_feature_name={has_feature_name}, "
            f"has_shap_value={has_shap_value}, "
            f"has_direction={has_direction}\n"
            f"Source:\n{source}"
        )

    @given(
        feature_pattern=sampled_from(FEATURE_NAME_PATTERNS),
        shap_pattern=sampled_from(SHAP_VALUE_PATTERNS),
        direction_pattern=sampled_from(DIRECTION_PATTERNS),
    )
    @settings(max_examples=100)
    def test_complete_response_always_detected(
        self, feature_pattern, shap_pattern, direction_pattern
    ):
        """Code with all three fields SHALL always be detected as complete.

        **Validates: Requirements 7.3**
        """
        source = "\n".join([
            "from pydantic import BaseModel",
            "",
            "class FeatureExplanation(BaseModel):",
            f"    {feature_pattern}",
            f"    {shap_pattern}",
            f"    {direction_pattern}",
            "",
        ]) + "\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ml_dir = tmpdir_path / "ml"
            ml_dir.mkdir()
            services_dir = tmpdir_path / "services"
            services_dir.mkdir()
            schemas_dir = tmpdir_path / "schemas"
            schemas_dir.mkdir()

            schema_file = schemas_dir / "explanations.py"
            schema_file.write_text(source, encoding="utf-8")

            phase = SHAPValidationPhase()
            result = phase._check_explanation_output_structure(
                ml_dir, services_dir, schemas_dir
            )

        assert result is True, (
            f"Expected complete response to be detected, but it was not.\n"
            f"Source:\n{source}"
        )

    @given(
        missing_field=sampled_from(["feature_name", "shap_value", "direction"]),
    )
    @settings(max_examples=100)
    def test_incomplete_response_missing_one_field(self, missing_field):
        """Code missing any single required field SHALL be detected as incomplete.

        **Validates: Requirements 7.3**
        """
        lines = [
            "from pydantic import BaseModel",
            "",
            "class FeatureExplanation(BaseModel):",
        ]

        if missing_field != "feature_name":
            lines.append("    feature_name: str")
        if missing_field != "shap_value":
            lines.append("    shap_value: float")
        if missing_field != "direction":
            lines.append("    direction: str")

        # Add an unrelated field to ensure the file isn't empty
        lines.append("    rank: int = 0")
        source = "\n".join(lines) + "\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ml_dir = tmpdir_path / "ml"
            ml_dir.mkdir()
            services_dir = tmpdir_path / "services"
            services_dir.mkdir()
            schemas_dir = tmpdir_path / "schemas"
            schemas_dir.mkdir()

            schema_file = schemas_dir / "explanations.py"
            schema_file.write_text(source, encoding="utf-8")

            phase = SHAPValidationPhase()
            result = phase._check_explanation_output_structure(
                ml_dir, services_dir, schemas_dir
            )

        assert result is False, (
            f"Expected incomplete response (missing '{missing_field}'), "
            f"but detection said complete.\n"
            f"Source:\n{source}"
        )
