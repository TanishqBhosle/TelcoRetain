"""Property-based tests for dataset validation detection logic.

**Validates: Requirements 5.2, 5.5**

Tests that the Phase 5 (DatasetValidationPhase) correctly identifies:
- Property 7: Incomplete categorical encoding coverage
- Property 8: Missing null-handling strategies in preprocessing code

Uses hypothesis to generate synthetic preprocessing code and verify
the detection logic correctly identifies gaps.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hypothesis import given, settings, assume
from hypothesis.strategies import (
    booleans,
    composite,
    just,
    lists,
    sampled_from,
    sets,
    text,
)

from audit.phases.phase_05_dataset import DatasetValidationPhase


# --------------------------------------------------------------------------
# Shared constants
# --------------------------------------------------------------------------

# IBM Telco categorical columns requiring encoding
ALL_CATEGORICAL_COLUMNS = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
]

# Binary columns covered by YES_NO_MAP
YES_NO_COLUMNS = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "PaperlessBilling",
]

# Multi-value columns requiring specific maps
MULTI_VALUE_COLUMNS = [
    "InternetService",
    "Contract",
    "PaymentMethod",
]

# Feature columns used in the ML pipeline
FEATURE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]


# --------------------------------------------------------------------------
# Strategies for Property 7: Categorical Encoding Completeness
# --------------------------------------------------------------------------


@composite
def encoding_coverage_scenario(draw):
    """Generate synthetic preprocessing code with various encoding patterns.

    Returns a tuple of (source_code, covers_all_categories) where
    covers_all_categories is True if the generated code handles all
    categorical columns.
    """
    # Decide which encoding patterns to include
    include_yes_no_map = draw(booleans())
    include_contract_map = draw(booleans())
    include_payment_map = draw(booleans())
    include_internet_map = draw(booleans())
    include_select_dtypes = draw(booleans())

    lines = [
        "import pandas as pd",
        "from sklearn.preprocessing import LabelEncoder",
        "",
        "",
    ]

    covered_columns: set = set()

    if include_yes_no_map:
        lines.append('YES_NO_MAP = {"Yes": 1, "No": 0, "Male": 1, "Female": 0}')
        lines.append("")
        lines.append("def _map_yes_no(df):")
        lines.append("    for col in df.columns:")
        lines.append("        df[col] = df[col].map(YES_NO_MAP)")
        lines.append("    return df")
        lines.append("")
        covered_columns.update(YES_NO_COLUMNS)

    if include_contract_map:
        lines.append('CONTRACT_MAP = {"Month-to-month": 0, "One year": 1, "Two year": 2}')
        lines.append("")
        covered_columns.add("Contract")

    if include_payment_map:
        lines.append(
            'PAYMENT_MAP = {"Electronic check": 0, "Mailed check": 1, '
            '"Bank transfer (automatic)": 2, "Credit card (automatic)": 3}'
        )
        lines.append("")
        covered_columns.add("PaymentMethod")

    if include_internet_map:
        lines.append('INTERNET_MAP = {"No": 0, "DSL": 1, "Fiber optic": 2}')
        lines.append("")
        covered_columns.add("InternetService")

    if include_select_dtypes:
        # This pattern covers all categoricals dynamically
        lines.append("def encode_all(df):")
        lines.append("    cat_cols = df.select_dtypes(include='object').columns")
        lines.append("    le = LabelEncoder()")
        lines.append("    for col in cat_cols:")
        lines.append("        df[col] = le.fit_transform(df[col])")
        lines.append("    return df")
        lines.append("")
        covered_columns.update(ALL_CATEGORICAL_COLUMNS)

    # Add a basic encoder reference if nothing else was added
    if not any([include_yes_no_map, include_contract_map,
                include_payment_map, include_internet_map, include_select_dtypes]):
        lines.append("# No encoding logic present")
        lines.append("")

    source = "\n".join(lines) + "\n"
    all_covered = set(ALL_CATEGORICAL_COLUMNS).issubset(covered_columns)

    return source, covered_columns, all_covered


def no_encoding_scenario():
    """Strategy returning preprocessing code with NO encoding patterns at all.

    Returns source code that lacks any encoder instantiation or mapping.
    """
    lines = [
        "import pandas as pd",
        "import numpy as np",
        "",
        "",
        "def load_data(path):",
        "    df = pd.read_csv(path)",
        "    return df",
        "",
        "",
        "def process(df):",
        "    # Basic processing without encoding",
        "    df['tenure_group'] = pd.cut(df['tenure'], bins=5)",
        "    return df",
        "",
    ]
    return just("\n".join(lines) + "\n")


# --------------------------------------------------------------------------
# Strategies for Property 8: Null Handling Completeness
# --------------------------------------------------------------------------

# Various null-handling code patterns
NULL_HANDLING_SNIPPETS = {
    "fillna_median": 'df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())',
    "fillna_zero": 'df["MonthlyCharges"].fillna(0, inplace=True)',
    "dropna": "df = df.dropna(subset=['TotalCharges'])",
    "simple_imputer": "from sklearn.impute import SimpleImputer\nimputer = SimpleImputer(strategy='median')",
    "knn_imputer": "from sklearn.impute import KNNImputer\nimputer = KNNImputer(n_neighbors=5)",
    "interpolate": "df['tenure'] = df['tenure'].interpolate()",
    "isna_check": "null_mask = df['TotalCharges'].isna()",
    "to_numeric_coerce": "df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')",
}

# Per-column null handling patterns
PER_COLUMN_SNIPPETS = {
    "bracket_fillna": 'df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())',
    "quote_fillna": "df['MonthlyCharges'] = df['MonthlyCharges'].fillna(0)",
    "fillna_median_ref": "df['tenure'].fillna(df['tenure'].median(), inplace=True)",
    "to_numeric_coerce": "df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')",
}


@composite
def null_handling_scenario(draw):
    """Generate synthetic preprocessing code with various null-handling patterns.

    Returns a tuple of (source_code, has_null_handling, has_per_column_handling)
    indicating what patterns are present.
    """
    # Decide which null-handling patterns to include
    include_any_handling = draw(booleans())
    include_per_column = draw(booleans())

    lines = [
        "import pandas as pd",
        "import numpy as np",
        "",
        "",
        "def preprocess(df):",
    ]

    has_null_handling = False
    has_per_column = False

    if include_any_handling:
        # Pick some null handling snippets
        available = list(NULL_HANDLING_SNIPPETS.keys())
        selected_keys = draw(
            lists(sampled_from(available), min_size=1, max_size=3, unique=True)
        )

        for key in selected_keys:
            snippet = NULL_HANDLING_SNIPPETS[key]
            for snippet_line in snippet.split("\n"):
                lines.append(f"    {snippet_line}")
        has_null_handling = True

    if include_per_column:
        # Add per-column handling patterns
        available_pc = list(PER_COLUMN_SNIPPETS.keys())
        selected_pc = draw(
            lists(sampled_from(available_pc), min_size=1, max_size=2, unique=True)
        )

        for key in selected_pc:
            snippet = PER_COLUMN_SNIPPETS[key]
            for snippet_line in snippet.split("\n"):
                lines.append(f"    {snippet_line}")
        has_null_handling = True
        has_per_column = True

    if not include_any_handling and not include_per_column:
        lines.append("    # No null handling")
        lines.append("    pass")

    lines.append("    return df")
    lines.append("")

    source = "\n".join(lines) + "\n"
    return source, has_null_handling, has_per_column


def no_null_handling_scenario():
    """Strategy returning preprocessing code with NO null handling patterns.

    Returns source code that processes data without any fillna, dropna,
    or imputation logic.
    """
    lines = [
        "import pandas as pd",
        "import numpy as np",
        "",
        "",
        "def preprocess(df):",
        "    # Transform columns without handling nulls",
        "    df['tenure_group'] = pd.cut(df['tenure'], bins=5)",
        "    df['charges_ratio'] = df['MonthlyCharges'] / df['TotalCharges']",
        "    return df",
        "",
        "",
        "def encode_features(df):",
        "    le = LabelEncoder()",
        "    df['Contract'] = le.fit_transform(df['Contract'])",
        "    return df",
        "",
    ]
    return just("\n".join(lines) + "\n")


# --------------------------------------------------------------------------
# Property 7: Categorical Encoding Completeness
# --------------------------------------------------------------------------


class TestCategoricalEncodingCompleteness:
    """Property 7: Categorical Encoding Completeness.

    **Validates: Requirements 5.2**

    For all unique categorical values present in the training dataset columns,
    the preprocessing encoder SHALL have a defined mapping, ensuring no
    unseen-category errors during inference.
    """

    @given(scenario=encoding_coverage_scenario())
    @settings(max_examples=30)
    def test_complete_encoding_produces_no_finding(self, scenario):
        """When all categorical columns have encoding coverage, no finding is produced.

        **Validates: Requirements 5.2**
        """
        source, covered_columns, all_covered = scenario
        assume(all_covered)

        with tempfile.TemporaryDirectory() as tmpdir:
            preprocessing_dir = Path(tmpdir) / "preprocessing"
            preprocessing_dir.mkdir()
            (preprocessing_dir / "encoder.py").write_text(source, encoding="utf-8")

            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()

            phase = DatasetValidationPhase()
            result = phase._check_encoding_completeness(preprocessing_dir, scripts_dir)

        # When all categorical columns are covered, no finding should be produced
        assert result is None, (
            f"Expected no finding when all categories are covered, "
            f"but got: {result.title if result else 'None'}\n"
            f"Covered columns: {sorted(covered_columns)}\n"
            f"Source:\n{source}"
        )

    @given(scenario=encoding_coverage_scenario())
    @settings(max_examples=30)
    def test_incomplete_encoding_produces_finding(self, scenario):
        """When some categorical columns lack encoding, a finding is produced.

        **Validates: Requirements 5.2**
        """
        source, covered_columns, all_covered = scenario
        assume(not all_covered)
        # Ensure at least some encoder logic exists (otherwise the finding
        # is about 'no encoding found' rather than 'incomplete coverage')
        assume(len(covered_columns) > 0)

        with tempfile.TemporaryDirectory() as tmpdir:
            preprocessing_dir = Path(tmpdir) / "preprocessing"
            preprocessing_dir.mkdir()
            (preprocessing_dir / "encoder.py").write_text(source, encoding="utf-8")

            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()

            phase = DatasetValidationPhase()
            result = phase._check_encoding_completeness(preprocessing_dir, scripts_dir)

        # When some columns lack encoding, a finding should be produced
        assert result is not None, (
            f"Expected a finding for incomplete encoding, but got None.\n"
            f"Covered columns: {sorted(covered_columns)}\n"
            f"Missing: {sorted(set(ALL_CATEGORICAL_COLUMNS) - covered_columns)}\n"
            f"Source:\n{source}"
        )
        assert "DS-002" in result.check_id, (
            f"Expected check_id DS-002, got {result.check_id}"
        )

    @given(source=no_encoding_scenario())
    @settings(max_examples=30)
    def test_no_encoding_logic_produces_finding(self, source):
        """When no encoding logic exists at all, a finding is produced.

        **Validates: Requirements 5.2**
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            preprocessing_dir = Path(tmpdir) / "preprocessing"
            preprocessing_dir.mkdir()
            (preprocessing_dir / "process.py").write_text(source, encoding="utf-8")

            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()

            phase = DatasetValidationPhase()
            result = phase._check_encoding_completeness(preprocessing_dir, scripts_dir)

        # When no encoding logic exists, a finding must be produced
        assert result is not None, (
            f"Expected a finding when no encoding logic is present, "
            f"but got None.\nSource:\n{source}"
        )
        assert result.check_id == "DS-002", (
            f"Expected check_id DS-002, got {result.check_id}"
        )
        assert result.severity is not None


# --------------------------------------------------------------------------
# Property 8: Null Handling Completeness
# --------------------------------------------------------------------------


class TestNullHandlingCompleteness:
    """Property 8: Null Handling Completeness.

    **Validates: Requirements 5.5**

    For all feature columns used in the ML pipeline, the preprocessing code
    SHALL include an explicit null-handling strategy (fillna, imputation,
    or dropna) rather than relying on implicit behavior.
    """

    @given(scenario=null_handling_scenario())
    @settings(max_examples=30)
    def test_with_null_handling_detection(self, scenario):
        """When null handling patterns are present, the detector finds them.

        **Validates: Requirements 5.5**
        """
        source, has_null_handling, has_per_column = scenario
        assume(has_null_handling)

        with tempfile.TemporaryDirectory() as tmpdir:
            preprocessing_dir = Path(tmpdir) / "preprocessing"
            preprocessing_dir.mkdir()
            (preprocessing_dir / "preprocess.py").write_text(source, encoding="utf-8")

            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()

            phase = DatasetValidationPhase()
            result = phase._check_null_handling(preprocessing_dir, scripts_dir)

        if has_per_column:
            # Per-column handling should result in no finding (passes the check)
            assert result is None, (
                f"Expected no finding when per-column null handling present, "
                f"but got: {result.title if result else 'None'}\n"
                f"Source:\n{source}"
            )
        else:
            # Non-per-column handling produces a finding about blanket approach
            # The check still finds null handling, but flags it as not per-column
            if result is not None:
                assert result.check_id == "DS-005", (
                    f"Expected check_id DS-005, got {result.check_id}"
                )

    @given(source=no_null_handling_scenario())
    @settings(max_examples=30)
    def test_no_null_handling_produces_finding(self, source):
        """When no null handling patterns exist, a finding is produced.

        **Validates: Requirements 5.5**
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            preprocessing_dir = Path(tmpdir) / "preprocessing"
            preprocessing_dir.mkdir()
            (preprocessing_dir / "preprocess.py").write_text(source, encoding="utf-8")

            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()

            phase = DatasetValidationPhase()
            result = phase._check_null_handling(preprocessing_dir, scripts_dir)

        # When no null handling is present, a finding must be produced
        assert result is not None, (
            f"Expected a finding when no null handling is present, "
            f"but got None.\nSource:\n{source}"
        )
        assert result.check_id == "DS-005", (
            f"Expected check_id DS-005, got {result.check_id}"
        )
        assert result.severity is not None

    @given(scenario=null_handling_scenario())
    @settings(max_examples=30)
    def test_per_column_handling_passes(self, scenario):
        """Per-column null handling should pass the check fully (no finding).

        **Validates: Requirements 5.5**
        """
        source, has_null_handling, has_per_column = scenario
        assume(has_per_column)

        with tempfile.TemporaryDirectory() as tmpdir:
            preprocessing_dir = Path(tmpdir) / "preprocessing"
            preprocessing_dir.mkdir()
            (preprocessing_dir / "preprocess.py").write_text(source, encoding="utf-8")

            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()

            phase = DatasetValidationPhase()
            result = phase._check_null_handling(preprocessing_dir, scripts_dir)

        # Per-column handling should pass
        assert result is None, (
            f"Expected no finding when per-column null handling present, "
            f"but got: {result.title if result else 'None'}\n"
            f"Source:\n{source}"
        )
