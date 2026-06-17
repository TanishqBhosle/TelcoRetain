"""Phase 5: Dataset Validation.

Validates the data pipeline including the training dataset, preprocessing
logic, and feature engineering for the IBM Telco Customer Churn dataset.

Checks:
- CSV schema existence and column validation against IBM Telco schema
- Categorical encoding completeness in preprocessing code
- Feature consistency between training and inference (train-serve skew)
- Dataset upload endpoint schema validation logic
- Null handling strategy per feature column
"""

import ast
import re
from pathlib import Path
from typing import Optional

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


# Expected columns in the IBM Telco Customer Churn dataset
IBM_TELCO_EXPECTED_COLUMNS = [
    "customerID",
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
    "Churn",
]


class DatasetValidationPhase(AuditPhase):
    """Phase 5: Dataset Validation.

    Inspects the training dataset, preprocessing logic, and feature
    engineering to verify data quality, encoding completeness, and
    consistency between training and inference pipelines.
    """

    name = "Dataset Validation"
    description = (
        "Validates the data pipeline including training dataset schema, "
        "preprocessing logic, feature consistency, and null handling."
    )

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute dataset validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all dataset checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 5
        passed_checks = 0

        backend_dir = workspace_root / "backend"
        data_dir = backend_dir / "data"
        ml_dir = backend_dir / "ml"
        preprocessing_dir = ml_dir / "preprocessing"
        inference_dir = ml_dir / "inference"
        scripts_dir = backend_dir / "scripts"
        api_dir = backend_dir / "app" / "api" / "v1"

        # Check 1: CSV schema validation
        csv_result = self._check_csv_schema(data_dir, backend_dir)
        if csv_result is None:
            passed_checks += 1
        else:
            findings.append(csv_result)

        # Check 2: Categorical encoding completeness
        encoding_result = self._check_encoding_completeness(
            preprocessing_dir, scripts_dir
        )
        if encoding_result is None:
            passed_checks += 1
        else:
            findings.append(encoding_result)

        # Check 3: Feature consistency (train-serve skew)
        skew_result = self._check_train_serve_skew(
            scripts_dir, preprocessing_dir, inference_dir
        )
        if skew_result is None:
            passed_checks += 1
        else:
            findings.append(skew_result)

        # Check 4: Dataset upload schema validation
        upload_result = self._check_upload_validation(api_dir, backend_dir)
        if upload_result is None:
            passed_checks += 1
        else:
            findings.append(upload_result)

        # Check 5: Null handling completeness
        null_result = self._check_null_handling(preprocessing_dir, scripts_dir)
        if null_result is None:
            passed_checks += 1
        else:
            findings.append(null_result)

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_csv_schema(
        self, data_dir: Path, backend_dir: Path
    ) -> Optional[AuditFinding]:
        """Check that the IBM Telco CSV exists and has expected columns.

        Attempts to load the CSV using pandas for full validation.
        Falls back to reading the header line if pandas is unavailable.

        Args:
            data_dir: Path to the data directory.
            backend_dir: Path to the backend directory.

        Returns:
            AuditFinding if check fails, None if it passes.
        """
        csv_filename = "WA_Fn-UseC_-Telco-Customer-Churn.csv"

        # Search common locations
        candidate_paths = [
            data_dir / csv_filename,
            backend_dir / "ml" / "data" / csv_filename,
            backend_dir / csv_filename,
        ]

        csv_path: Optional[Path] = None
        for candidate in candidate_paths:
            if candidate.exists():
                csv_path = candidate
                break

        if csv_path is None:
            return AuditFinding(
                phase=self.name,
                check_id="DS-001",
                title="Training dataset file not found",
                severity=Severity.HIGH,
                description=(
                    f"Could not find '{csv_filename}' in any expected "
                    f"location (data/, ml/data/, backend root). "
                    f"Searched: {[str(p) for p in candidate_paths]}"
                ),
                recommendation=(
                    "Ensure the IBM Telco Customer Churn dataset is "
                    "available at backend/data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
                ),
            )

        # Try to validate columns
        actual_columns = self._read_csv_columns(csv_path)
        if actual_columns is None:
            return AuditFinding(
                phase=self.name,
                check_id="DS-001",
                title="Training dataset file is not parseable",
                severity=Severity.HIGH,
                description=(
                    f"Found '{csv_filename}' at {csv_path} but could not "
                    f"parse it as a valid CSV file."
                ),
                file_path=str(csv_path),
                recommendation=(
                    "Verify the CSV file is not corrupted and contains "
                    "valid comma-separated data with a header row."
                ),
            )

        # Compare against expected columns
        expected_set = set(IBM_TELCO_EXPECTED_COLUMNS)
        actual_set = set(actual_columns)
        missing_columns = expected_set - actual_set

        if missing_columns:
            return AuditFinding(
                phase=self.name,
                check_id="DS-001",
                title="Training dataset missing expected columns",
                severity=Severity.HIGH,
                description=(
                    f"The CSV file is missing {len(missing_columns)} "
                    f"expected IBM Telco columns: {sorted(missing_columns)}. "
                    f"Found {len(actual_columns)} columns total."
                ),
                file_path=str(csv_path),
                recommendation=(
                    "Ensure the dataset contains all standard IBM Telco "
                    "Customer Churn columns including customerID, gender, "
                    "SeniorCitizen, tenure, etc."
                ),
            )

        return None

    def _read_csv_columns(self, csv_path: Path) -> Optional[list[str]]:
        """Read column names from a CSV file.

        Attempts pandas first, falls back to reading the header line.

        Args:
            csv_path: Path to the CSV file.

        Returns:
            List of column names, or None if file cannot be parsed.
        """
        # Try pandas first
        try:
            import pandas as pd

            df = pd.read_csv(csv_path, nrows=0)
            return list(df.columns)
        except ImportError:
            pass
        except Exception:
            pass

        # Fallback: read just the header line
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                header_line = f.readline().strip()
            if not header_line:
                return None
            columns = [col.strip().strip('"') for col in header_line.split(",")]
            return columns if columns else None
        except (OSError, UnicodeDecodeError):
            return None

    def _check_encoding_completeness(
        self, preprocessing_dir: Path, scripts_dir: Path
    ) -> Optional[AuditFinding]:
        """Check that preprocessing code handles all categorical encodings.

        Looks for encoder instantiation (LabelEncoder, OneHotEncoder,
        OrdinalEncoder) and verifies category mapping coverage.

        Args:
            preprocessing_dir: Path to the ML preprocessing directory.
            scripts_dir: Path to the scripts directory.

        Returns:
            AuditFinding if check fails, None if it passes.
        """
        search_dirs = [preprocessing_dir, scripts_dir]
        encoder_patterns = [
            r"LabelEncoder",
            r"OneHotEncoder",
            r"OrdinalEncoder",
        ]
        mapping_patterns = [
            r"\w+_MAP\s*=",
            r"YES_NO_MAP",
            r"CONTRACT_MAP",
            r"PAYMENT_MAP",
            r"INTERNET_MAP",
            r"\.fit_transform\(",
            r"\.fit\(",
        ]

        encoder_found = False
        mapping_found = False

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                for pattern in encoder_patterns:
                    if re.search(pattern, content):
                        encoder_found = True
                        break

                for pattern in mapping_patterns:
                    if re.search(pattern, content):
                        mapping_found = True
                        break

        if not encoder_found and not mapping_found:
            return AuditFinding(
                phase=self.name,
                check_id="DS-002",
                title="No categorical encoding logic found",
                severity=Severity.MEDIUM,
                description=(
                    "Could not find encoder instantiation (LabelEncoder, "
                    "OneHotEncoder, OrdinalEncoder) or category mapping "
                    "definitions in preprocessing or training code."
                ),
                recommendation=(
                    "Implement explicit categorical encoding with defined "
                    "mappings for all categorical columns to prevent "
                    "unseen-category errors during inference."
                ),
            )

        # Check if all known categorical columns have coverage
        # IBM Telco categorical columns that need encoding
        categorical_columns = {
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
        }

        covered_columns = self._find_covered_categorical_columns(
            preprocessing_dir, scripts_dir
        )
        uncovered = categorical_columns - covered_columns

        if uncovered:
            return AuditFinding(
                phase=self.name,
                check_id="DS-002",
                title="Incomplete categorical encoding coverage",
                severity=Severity.MEDIUM,
                description=(
                    f"Found encoder logic but {len(uncovered)} categorical "
                    f"column(s) may lack explicit category mapping: "
                    f"{sorted(uncovered)}. The training script uses "
                    f"LabelEncoder.fit_transform() which covers all "
                    f"categories at training time, but the inference "
                    f"pipeline uses hardcoded mappings that may miss "
                    f"categories."
                ),
                recommendation=(
                    "Ensure all unique categorical values from the training "
                    "data are explicitly mapped in the inference pipeline "
                    "to prevent unseen-category errors."
                ),
            )

        return None

    def _find_covered_categorical_columns(
        self, preprocessing_dir: Path, scripts_dir: Path
    ) -> set[str]:
        """Find which categorical columns have explicit encoding coverage.

        Args:
            preprocessing_dir: Path to preprocessing directory.
            scripts_dir: Path to scripts directory.

        Returns:
            Set of column names with explicit encoding.
        """
        covered: set[str] = set()
        search_dirs = [preprocessing_dir, scripts_dir]

        # Patterns that indicate a column is being encoded
        # Look for column names referenced in encoding contexts
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                # Check for explicit map references
                if "CONTRACT_MAP" in content or "'Contract'" in content or '"Contract"' in content:
                    covered.add("Contract")
                if "PAYMENT_MAP" in content or "'PaymentMethod'" in content or '"PaymentMethod"' in content:
                    covered.add("PaymentMethod")
                if "INTERNET_MAP" in content or "'InternetService'" in content or '"InternetService"' in content:
                    covered.add("InternetService")
                if "YES_NO_MAP" in content or "_map_yes_no" in content:
                    # YES_NO_MAP covers binary categorical columns
                    covered.update({
                        "gender", "Partner", "Dependents", "PhoneService",
                        "MultipleLines", "OnlineSecurity", "OnlineBackup",
                        "DeviceProtection", "TechSupport", "StreamingTV",
                        "StreamingMovies", "PaperlessBilling",
                    })

                # Check for generic fit_transform on all object columns
                if "select_dtypes" in content and "fit_transform" in content:
                    # This pattern covers all categorical columns dynamically
                    covered.update({
                        "gender", "Partner", "Dependents", "PhoneService",
                        "MultipleLines", "InternetService", "OnlineSecurity",
                        "OnlineBackup", "DeviceProtection", "TechSupport",
                        "StreamingTV", "StreamingMovies", "Contract",
                        "PaperlessBilling", "PaymentMethod",
                    })

        return covered

    def _check_train_serve_skew(
        self,
        scripts_dir: Path,
        preprocessing_dir: Path,
        inference_dir: Path,
    ) -> Optional[AuditFinding]:
        """Compare feature columns between training and inference pipelines.

        Detects train-serve skew by comparing the feature column lists
        defined in the training script vs the inference pipeline.

        Args:
            scripts_dir: Path to the scripts directory.
            preprocessing_dir: Path to the preprocessing directory.
            inference_dir: Path to the inference directory.

        Returns:
            AuditFinding if skew is detected, None if consistent.
        """
        training_features = self._extract_feature_list_from_dir(scripts_dir)
        inference_features = self._extract_feature_list_from_dir(
            preprocessing_dir
        )

        if not training_features:
            # Try inference dir as fallback
            if not inference_features:
                return AuditFinding(
                    phase=self.name,
                    check_id="DS-003",
                    title="Cannot determine feature columns for skew analysis",
                    severity=Severity.MEDIUM,
                    description=(
                        "Could not extract feature column definitions from "
                        "either the training script or inference pipeline "
                        "to perform train-serve skew comparison."
                    ),
                    recommendation=(
                        "Define an explicit FEATURE_COLUMNS list in both "
                        "training and inference code to enable automated "
                        "consistency verification."
                    ),
                )
            return None

        if not inference_features:
            return AuditFinding(
                phase=self.name,
                check_id="DS-003",
                title="No feature column definition in inference pipeline",
                severity=Severity.HIGH,
                description=(
                    "Training script defines feature columns but the "
                    "inference/preprocessing pipeline does not have an "
                    "explicit feature column list for comparison."
                ),
                recommendation=(
                    "Define an explicit FEATURE_COLUMNS list in the "
                    "inference pipeline that matches the training features."
                ),
            )

        # Compare the two feature lists
        training_set = set(training_features)
        inference_set = set(inference_features)

        in_training_only = training_set - inference_set
        in_inference_only = inference_set - training_set

        if in_training_only or in_inference_only:
            details = []
            if in_training_only:
                details.append(
                    f"In training only: {sorted(in_training_only)}"
                )
            if in_inference_only:
                details.append(
                    f"In inference only: {sorted(in_inference_only)}"
                )
            return AuditFinding(
                phase=self.name,
                check_id="DS-003",
                title="Train-serve feature skew detected",
                severity=Severity.HIGH,
                description=(
                    f"Feature columns differ between training "
                    f"({len(training_features)} features) and inference "
                    f"({len(inference_features)} features). "
                    + " | ".join(details)
                ),
                recommendation=(
                    "Align feature columns between training and inference "
                    "pipelines. Use a shared feature column definition "
                    "to prevent train-serve skew."
                ),
            )

        return None

    def _extract_feature_list_from_dir(
        self, directory: Path
    ) -> Optional[list[str]]:
        """Extract TELCO_FEATURE_COLUMNS or similar list from Python files.

        Searches for a module-level list assignment containing feature
        column names. Prioritizes lists with 'TELCO' in the name, then
        falls back to any feature/column list.

        Args:
            directory: Directory to search for feature column definitions.

        Returns:
            List of feature column names, or None if not found.
        """
        if not directory.exists():
            return None

        # Collect all candidates: (priority, features)
        # Lower priority number = higher priority
        candidates: list[tuple[int, list[str]]] = []

        for py_file in directory.rglob("*.py"):
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                if not node.targets:
                    continue
                target = node.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                # Look for lists named *FEATURE* or *COLUMNS*
                name_upper = target.id.upper()
                if "FEATURE" in name_upper or "COLUMNS" in name_upper:
                    features = self._extract_string_list(node.value)
                    if features:
                        # Prioritize TELCO-specific lists
                        if "TELCO" in name_upper:
                            candidates.append((0, features))
                        else:
                            candidates.append((1, features))

        if not candidates:
            return None

        # Return highest priority (lowest number) candidate
        candidates.sort(key=lambda c: c[0])
        return candidates[0][1]

    def _extract_string_list(self, node: ast.expr) -> Optional[list[str]]:
        """Extract a list of string constants from an AST node.

        Args:
            node: AST expression node (expected to be a List).

        Returns:
            List of string values, or None if not a string list.
        """
        if not isinstance(node, ast.List):
            return None

        result: list[str] = []
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                result.append(elt.value)
            else:
                # Not a pure string list
                return None

        return result if result else None

    def _check_upload_validation(
        self, api_dir: Path, backend_dir: Path
    ) -> Optional[AuditFinding]:
        """Check dataset upload endpoint for schema validation logic.

        Verifies that uploaded datasets are validated for schema
        conformance before processing (column names, types, etc.).

        Args:
            api_dir: Path to the API v1 router directory.
            backend_dir: Path to the backend directory.

        Returns:
            AuditFinding if schema validation is missing, None if present.
        """
        datasets_router = api_dir / "datasets.py"
        service_file = backend_dir / "app" / "services" / "dataset_service.py"

        # Search for schema validation patterns in dataset-related files
        validation_patterns = [
            r"columns?\s*==",
            r"expected_columns",
            r"schema.*valid",
            r"validate.*schema",
            r"validate.*columns",
            r"required_columns",
            r"column.*check",
        ]

        files_to_check = [datasets_router, service_file]
        has_schema_validation = False

        for file_path in files_to_check:
            if not file_path.exists():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for pattern in validation_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    has_schema_validation = True
                    break
            if has_schema_validation:
                break

        if not has_schema_validation:
            # Also check if there's file type/size validation (basic level)
            has_basic_validation = False
            for file_path in files_to_check:
                if not file_path.exists():
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                # Check for at least file type validation
                if re.search(
                    r"ALLOWED_EXTENSIONS|file.*type|extension", content
                ):
                    has_basic_validation = True
                    break

            description = (
                "The dataset upload endpoint does not validate uploaded "
                "CSV column schema before processing. "
            )
            if has_basic_validation:
                description += (
                    "File type and size validation is present, but "
                    "column/schema validation is missing."
                )
            else:
                description += (
                    "Neither file type nor column schema validation "
                    "was found."
                )

            return AuditFinding(
                phase=self.name,
                check_id="DS-004",
                title="Missing schema validation on dataset upload",
                severity=Severity.MEDIUM,
                description=description,
                file_path=str(datasets_router),
                recommendation=(
                    "Add column schema validation to the dataset upload "
                    "endpoint to verify uploaded files contain expected "
                    "columns before processing and storing."
                ),
            )

        return None

    def _check_null_handling(
        self, preprocessing_dir: Path, scripts_dir: Path
    ) -> Optional[AuditFinding]:
        """Check preprocessing for explicit null-handling strategy.

        Looks for fillna, imputation, dropna, or default value patterns
        to ensure null values are handled explicitly rather than relying
        on implicit behavior.

        Args:
            preprocessing_dir: Path to preprocessing directory.
            scripts_dir: Path to scripts directory.

        Returns:
            AuditFinding if null handling is implicit, None if explicit.
        """
        null_handling_patterns = [
            r"\.fillna\(",
            r"\.dropna\(",
            r"SimpleImputer",
            r"KNNImputer",
            r"IterativeImputer",
            r"\.interpolate\(",
            r"\.replace\(.*[Nn]a[Nn]",
            r"pd\.to_numeric\(.*errors\s*=\s*['\"]coerce['\"]",
            r"isnull\(\)",
            r"isna\(\)",
            r"notna\(\)",
        ]

        default_value_patterns = [
            r"if\s+\w+\s+is\s+None",
            r"or\s+0",
            r"getattr\(.*,\s*\d+\)",
            r"\?\?",  # TypeScript null coalescing (if checking TS too)
        ]

        search_dirs = [preprocessing_dir, scripts_dir]
        null_handlers_found: list[str] = []
        files_with_handling: set[str] = set()

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                for pattern in null_handling_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        null_handlers_found.extend(matches)
                        files_with_handling.add(py_file.name)

                for pattern in default_value_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        null_handlers_found.extend(matches)
                        files_with_handling.add(py_file.name)

        if not null_handlers_found:
            return AuditFinding(
                phase=self.name,
                check_id="DS-005",
                title="No explicit null handling in preprocessing",
                severity=Severity.MEDIUM,
                description=(
                    "Could not find explicit null-handling strategy "
                    "(fillna, imputation, dropna) in preprocessing or "
                    "training code. Null values may cause errors or "
                    "produce unexpected model behavior."
                ),
                recommendation=(
                    "Add explicit null-handling strategy per feature column "
                    "(fillna with median/mode, imputation, or documented "
                    "dropna) rather than relying on implicit behavior."
                ),
            )

        # Check if null handling covers all feature columns or is
        # generic (e.g., just a single dropna at the end)
        has_per_column = self._has_per_column_null_handling(
            preprocessing_dir, scripts_dir
        )

        if not has_per_column:
            return AuditFinding(
                phase=self.name,
                check_id="DS-005",
                title="Null handling is not per-column explicit",
                severity=Severity.MEDIUM,
                description=(
                    f"Found null handling in {sorted(files_with_handling)} "
                    f"but it appears to use blanket approaches (dropna on "
                    f"entire DataFrame, or single fillna) rather than "
                    f"per-column strategies. Columns like TotalCharges "
                    f"may need median imputation while others need mode."
                ),
                recommendation=(
                    "Implement per-column null handling: use median for "
                    "numeric columns (MonthlyCharges, TotalCharges, tenure) "
                    "and mode/default for categorical columns."
                ),
            )

        return None

    def _has_per_column_null_handling(
        self, preprocessing_dir: Path, scripts_dir: Path
    ) -> bool:
        """Check if null handling is applied per-column.

        Looks for patterns like df['col'].fillna() or column-specific
        imputation rather than just df.dropna().

        Args:
            preprocessing_dir: Path to preprocessing directory.
            scripts_dir: Path to scripts directory.

        Returns:
            True if per-column handling is found.
        """
        per_column_patterns = [
            r"\[\"?\w+\"?\]\.fillna\(",
            r"\['\w+'\]\.fillna\(",
            r"df\[.*\]\s*=\s*df\[.*\]\.fillna\(",
            r"fillna\(df\[.*\]\.median\(\)",
            r"fillna\(df\[.*\]\.mean\(\)",
            r"fillna\(.*median",
            r"\"TotalCharges\"\].*fillna",
            r"'TotalCharges'\].*fillna",
            r"to_numeric.*coerce",
        ]

        search_dirs = [preprocessing_dir, scripts_dir]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                for pattern in per_column_patterns:
                    if re.search(pattern, content):
                        return True

        return False
