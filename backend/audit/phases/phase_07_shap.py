"""Phase 7: SHAP Validation.

Validates SHAP explainability implementation including TreeExplainer
instantiation, explanation output structure, edge case handling,
and reason map coverage.

Checks:
- TreeExplainer instantiation with correct model object
- Explanation output structure (feature_name, shap_value, direction)
- Edge case handling (zero-variance features, missing features)
- Reason map coverage of top features from training data
- SHAP additivity validation in code
"""

import ast
import re
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class SHAPValidationPhase(AuditPhase):
    """Phase 7: SHAP Validation.

    Inspects the SHAP explainer code and explanation service to verify
    correct TreeExplainer usage, output structure completeness, edge case
    handling, and reason map coverage.
    """

    name = "SHAP Validation"
    description = (
        "Validates SHAP explainability implementation for correctness, "
        "completeness, and robustness."
    )

    # Expected fields in explanation output
    REQUIRED_EXPLANATION_FIELDS = {"feature_name", "shap_value"}
    DIRECTION_INDICATORS = {"direction", "increases_churn", "decreases_churn"}

    # Key features that should be mapped in the reason_map
    EXPECTED_REASON_MAP_FEATURES = {
        "tenure_months",
        "monthly_charges",
        "total_charges",
        "complaints_count",
        "call_drop_rate",
        "signal_strength",
    }

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute SHAP validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all SHAP checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 5
        passed_checks = 0

        ml_dir = workspace_root / "backend" / "ml"
        services_dir = workspace_root / "backend" / "app" / "services"
        schemas_dir = workspace_root / "backend" / "app" / "schemas"

        # Check 1: TreeExplainer instantiation with correct model object
        tree_explainer_ok = self._check_tree_explainer_instantiation(
            ml_dir, services_dir
        )
        if tree_explainer_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="SHAP-001",
                    title="Missing or incorrect TreeExplainer instantiation",
                    severity=Severity.HIGH,
                    description=(
                        "Could not verify that shap.TreeExplainer is "
                        "instantiated with the correct model object. "
                        "The SHAP explainer should be created with "
                        "shap.TreeExplainer(model) where model is the "
                        "loaded ML model artifact."
                    ),
                    recommendation=(
                        "Ensure shap.TreeExplainer is instantiated with "
                        "the loaded model object (e.g., self._model) in "
                        "the explainer code."
                    ),
                )
            )

        # Check 2: SHAP additivity validation in code
        additivity_ok = self._check_additivity_validation(
            ml_dir, services_dir
        )
        if additivity_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="SHAP-002",
                    title="No SHAP additivity validation found",
                    severity=Severity.MEDIUM,
                    description=(
                        "No code was found that validates the SHAP additivity "
                        "property (sum of SHAP values + base_value ≈ prediction). "
                        "This is a mathematical property that ensures SHAP "
                        "explanations are consistent with model predictions."
                    ),
                    recommendation=(
                        "Add a validation step that checks: "
                        "sum(shap_values) + base_value ≈ model_prediction "
                        "within a small tolerance (e.g., ±0.01)."
                    ),
                )
            )

        # Check 3: Explanation output structure
        output_structure_ok = self._check_explanation_output_structure(
            ml_dir, services_dir, schemas_dir
        )
        if output_structure_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="SHAP-003",
                    title="Incomplete explanation output structure",
                    severity=Severity.MEDIUM,
                    description=(
                        "The explanation output does not include all required "
                        "fields: feature_name, shap_value, and direction "
                        "(positive/negative contribution indicator). Each "
                        "explanation item should clearly communicate the "
                        "feature name, its SHAP value, and whether it "
                        "increases or decreases the prediction."
                    ),
                    recommendation=(
                        "Ensure each explanation response item includes "
                        "'feature_name' (string), 'shap_value' (numeric), "
                        "and a 'direction' indicator (e.g., "
                        "'increases_churn'/'decreases_churn')."
                    ),
                )
            )

        # Check 4: Edge case handling
        edge_case_ok = self._check_edge_case_handling(ml_dir, services_dir)
        if edge_case_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="SHAP-004",
                    title="Missing edge case handling in SHAP computation",
                    severity=Severity.MEDIUM,
                    description=(
                        "The SHAP computation code does not adequately "
                        "handle edge cases such as zero-variance features, "
                        "missing features, or invalid inputs. The explainer "
                        "should gracefully handle these scenarios without "
                        "raising unhandled exceptions."
                    ),
                    recommendation=(
                        "Add try/except blocks and conditional checks for: "
                        "1) features with zero variance, "
                        "2) missing feature values (use default/fill), "
                        "3) invalid input types. Return empty or partial "
                        "explanations rather than crashing."
                    ),
                )
            )

        # Check 5: Reason map coverage
        reason_map_ok = self._check_reason_map_coverage(ml_dir, services_dir)
        if reason_map_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="SHAP-005",
                    title="Incomplete reason map for top SHAP features",
                    severity=Severity.MEDIUM,
                    description=(
                        "The reason_map or feature-to-reason mapping does "
                        "not cover all expected top features from the "
                        "training data. Unmapped features will produce "
                        "generic or missing explanations for users."
                    ),
                    recommendation=(
                        "Extend the reason_map to include human-readable "
                        "descriptions for all top features used by the "
                        "model, particularly: tenure, monthly charges, "
                        "total charges, complaints, call drops, and "
                        "signal strength."
                    ),
                )
            )

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_tree_explainer_instantiation(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Verify TreeExplainer is instantiated with a model object.

        Searches for shap.TreeExplainer(self._model) or similar patterns
        in the ML explainability code and services.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if TreeExplainer instantiation with model is found.
        """
        search_dirs = [ml_dir, services_dir]
        pattern = r"TreeExplainer\s*\("

        for directory in search_dirs:
            if not directory.exists():
                continue
            matches = StaticAnalyzer.grep_pattern(
                directory, pattern, [".py"]
            )
            for file_path, line_no, line_content in matches:
                # Verify it's called with a model object (not empty)
                if re.search(
                    r"TreeExplainer\s*\(\s*self[._]\w+", line_content
                ):
                    return True
                # Also accept variable references
                if re.search(
                    r"TreeExplainer\s*\(\s*\w+", line_content
                ) and "TreeExplainer()" not in line_content:
                    return True

        return False

    def _check_additivity_validation(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Check for SHAP additivity validation in code.

        Looks for code that validates the sum of SHAP values equals
        prediction minus base value, or checks related to additivity.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if additivity validation logic is found.
        """
        search_dirs = [ml_dir, services_dir]
        # Look for patterns related to additivity checking
        additivity_patterns = [
            r"base_value",
            r"expected_value",
            r"additivity",
            r"shap_values.*sum",
            r"sum.*shap_values",
            r"np\.isclose.*shap",
            r"abs.*prediction.*base",
        ]

        for directory in search_dirs:
            if not directory.exists():
                continue
            for pattern in additivity_patterns:
                matches = StaticAnalyzer.grep_pattern(
                    directory, pattern, [".py"]
                )
                if matches:
                    return True

        return False

    def _check_explanation_output_structure(
        self, ml_dir: Path, services_dir: Path, schemas_dir: Path
    ) -> bool:
        """Verify explanation output includes required fields.

        Checks both the schema definitions and the actual output
        construction for feature_name, shap_value, and direction fields.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.
            schemas_dir: Path to the schemas directory.

        Returns:
            True if all required fields are present in output structure.
        """
        has_feature_name = False
        has_shap_value = False
        has_direction = False

        search_dirs = [ml_dir, services_dir, schemas_dir]

        for directory in search_dirs:
            if not directory.exists():
                continue

            # Check for feature_name field
            matches = StaticAnalyzer.grep_pattern(
                directory, r"feature_name", [".py"]
            )
            if matches:
                has_feature_name = True

            # Check for shap_value field
            matches = StaticAnalyzer.grep_pattern(
                directory, r"shap_value", [".py"]
            )
            if matches:
                has_shap_value = True

            # Check for direction indicator
            direction_patterns = [
                r"direction",
                r"increases_churn|decreases_churn",
                r"positive.*contribution|negative.*contribution",
            ]
            for pattern in direction_patterns:
                matches = StaticAnalyzer.grep_pattern(
                    directory, pattern, [".py"]
                )
                if matches:
                    has_direction = True
                    break

        return has_feature_name and has_shap_value and has_direction

    def _check_edge_case_handling(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Check for edge case handling in SHAP computation.

        Looks for try/except blocks, conditional checks for None/empty,
        default value handling, and zero-variance checks around SHAP
        computation code.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if adequate edge case handling is found.
        """
        search_dirs = [ml_dir, services_dir]
        edge_case_indicators = 0

        for directory in search_dirs:
            if not directory.exists():
                continue

            # Look for try/except around SHAP computation
            shap_files = list(directory.rglob("*shap*")) + list(
                directory.rglob("*explain*")
            )
            for shap_file in shap_files:
                if not shap_file.is_file() or not shap_file.suffix == ".py":
                    continue
                try:
                    tree = StaticAnalyzer.parse_python_module(shap_file)
                except (SyntaxError, FileNotFoundError):
                    continue

                # Check for try/except blocks
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        # Check if body contains SHAP-related code
                        try_source = ast.dump(node)
                        if any(
                            kw in try_source
                            for kw in ["shap", "explainer", "explain"]
                        ):
                            edge_case_indicators += 1

                # Check for None/empty checks
                matches = StaticAnalyzer.grep_pattern(
                    directory,
                    r"if.*(?:None|not\s+\w+|is\s+None|\[\]|==\s*\[\])",
                    [".py"],
                )
                for _, _, line in matches:
                    if any(
                        kw in line.lower()
                        for kw in [
                            "explainer",
                            "feature",
                            "shap",
                            "model",
                        ]
                    ):
                        edge_case_indicators += 1

            # Check for default/fallback values for missing features
            matches = StaticAnalyzer.grep_pattern(
                directory, r"\.get\(\s*\w+\s*,\s*0\s*\)", [".py"]
            )
            if matches:
                edge_case_indicators += 1

        # Require at least 2 indicators of edge case handling
        return edge_case_indicators >= 2

    def _check_reason_map_coverage(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Verify reason_map covers top features from training data.

        Checks that the mapping from feature names to human-readable
        descriptions covers the expected key features.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if reason_map covers sufficient key features.
        """
        search_dirs = [ml_dir, services_dir]
        mapped_features: set[str] = set()

        for directory in search_dirs:
            if not directory.exists():
                continue

            # Look for reason_map dictionary or _map_to_business_reason
            py_files = list(directory.rglob("*.py"))
            for py_file in py_files:
                if not py_file.is_file():
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                # Check for dictionary-style reason_map
                if "reason_map" in content or "_map_to_business_reason" in content:
                    # Extract keys from dict literal or if-conditions
                    # Pattern: "feature_name": "description"
                    dict_keys = re.findall(
                        r'["\'](\w+)["\']\s*:', content
                    )
                    mapped_features.update(dict_keys)

                    # Pattern: if "feature" in feat_lower
                    condition_keys = re.findall(
                        r'if\s+["\'](\w+)["\']\s+in\s+\w+', content
                    )
                    mapped_features.update(condition_keys)

                    # Pattern: "feature" in feat_lower or variable
                    in_checks = re.findall(
                        r'["\'](\w+)["\']\s+in\s+feat', content
                    )
                    mapped_features.update(in_checks)

        # Check coverage - at least 60% of expected features should be mapped
        if not mapped_features:
            return False

        covered = 0
        for expected in self.EXPECTED_REASON_MAP_FEATURES:
            # Check if any mapped feature contains the expected feature name
            for mapped in mapped_features:
                if expected in mapped or mapped in expected:
                    covered += 1
                    break

        coverage_ratio = covered / len(self.EXPECTED_REASON_MAP_FEATURES)
        return coverage_ratio >= 0.6
