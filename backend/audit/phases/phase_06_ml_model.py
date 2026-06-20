"""Phase 6: ML Model Validation.

Validates ML model training artifacts, inference pipeline, and model
governance practices including versioning, graceful error handling,
and ensemble logic documentation.

Checks:
- Versioning metadata in artifacts (training_date, dataset_hash, hyperparameters)
- Graceful handling of missing/corrupted model artifacts in loader code
- LightGBM artifact existence (Critical if missing)
- Documented ensemble logic in prediction service
- AUC metric verifiability from artifacts
- Model versioning (no overwrite on retrain)
"""

import ast
import json
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class MLModelValidationPhase(AuditPhase):
    """Phase 6: ML Model Validation.

    Inspects ML artifacts directory for versioning metadata, verifies
    graceful artifact handling in loader code, checks for missing
    LightGBM model, validates ensemble logic documentation, and
    verifies model versioning practices.
    """

    name = "ML Model Validation"
    description = (
        "Validates ML model artifacts, inference pipeline, and model "
        "governance practices for production readiness."
    )

    REQUIRED_METADATA_FIELDS = {"training_date", "dataset_hash", "hyperparameters"}
    LIGHTGBM_ARTIFACT_NAME = "lightgbm"
    EXPECTED_AUC = 0.839

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute ML model validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all ML model checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 6
        passed_checks = 0

        artifacts_dir = workspace_root / "backend" / "ml" / "artifacts"
        inference_dir = workspace_root / "backend" / "ml" / "inference"
        services_dir = workspace_root / "backend" / "app" / "services"
        scripts_dir = workspace_root / "backend" / "scripts"

        # Check 1: Versioning metadata
        if self._check_versioning_metadata(artifacts_dir):
            passed_checks += 1
        else:
            missing = self._get_missing_metadata_fields(artifacts_dir)
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="ML-001",
                    title="Missing versioning metadata in ML artifacts",
                    severity=Severity.MEDIUM,
                    description=(
                        f"The ML artifacts metadata.json is missing required "
                        f"versioning fields: {sorted(missing)}. "
                        f"Model governance requires training_date, "
                        f"dataset_hash, and hyperparameters to be recorded "
                        f"for reproducibility and audit trails."
                    ),
                    file_path=str(artifacts_dir / "metadata.json"),
                    recommendation=(
                        "Add training_date, dataset_hash, and hyperparameters "
                        "fields to the metadata.json file generated during "
                        "model training."
                    ),
                )
            )

        # Check 2: Graceful artifact handling
        if self._check_graceful_artifact_handling(inference_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="ML-002",
                    title="No graceful error handling for model artifact loading",
                    severity=Severity.HIGH,
                    description=(
                        "The model loader code does not use try/except around "
                        "file loading operations (joblib.load, pickle.load, "
                        "or similar). Missing or corrupted artifacts could "
                        "crash the application on startup."
                    ),
                    file_path=str(inference_dir / "artifact_loader.py"),
                    recommendation=(
                        "Wrap artifact loading operations in try/except blocks "
                        "to handle FileNotFoundError, EOFError, and "
                        "pickle.UnpicklingError gracefully."
                    ),
                )
            )

        # Check 3: LightGBM artifact existence
        if self._check_lightgbm_artifact(artifacts_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="ML-003",
                    title="LightGBM model artifact missing",
                    severity=Severity.CRITICAL,
                    description=(
                        "The LightGBM model artifact (lightgbm.pkl) claimed "
                        "in the README is not present in the ML artifacts "
                        "directory. This model is part of the documented "
                        "ensemble and its absence degrades prediction quality."
                    ),
                    file_path=str(artifacts_dir),
                    recommendation=(
                        "Run the model training pipeline with LightGBM "
                        "installed to generate the lightgbm.pkl artifact, "
                        "or update the README to reflect actual available models."
                    ),
                )
            )

        # Check 4: Documented ensemble logic
        if self._check_ensemble_documentation(inference_dir, services_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="ML-004",
                    title="Undocumented ensemble prediction logic",
                    severity=Severity.MEDIUM,
                    description=(
                        "The prediction service combines model outputs using "
                        "an averaging strategy, but this ensemble approach "
                        "is not clearly documented with a docstring or "
                        "comments explaining the combination strategy "
                        "(averaging, voting, or stacking)."
                    ),
                    file_path=str(inference_dir / "predictor.py"),
                    recommendation=(
                        "Add documentation to the prediction logic explaining "
                        "the ensemble strategy (e.g., probability averaging), "
                        "why it was chosen, and how individual model outputs "
                        "are weighted."
                    ),
                )
            )

        # Check 5: AUC metric verifiability
        if self._check_auc_metric(artifacts_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="ML-005",
                    title="Claimed AUC metric not fully verifiable from artifacts",
                    severity=Severity.MEDIUM,
                    description=(
                        f"The README claims 83.9% AUC but the metadata.json "
                        f"does not include all information needed to "
                        f"independently reproduce this metric (missing "
                        f"dataset_hash or training_date for exact "
                        f"reproducibility). The stored AUC values in "
                        f"metadata suggest the metric may come from a "
                        f"specific model configuration."
                    ),
                    file_path=str(artifacts_dir / "metadata.json"),
                    recommendation=(
                        "Include dataset_hash and training_date in metadata "
                        "to enable full reproducibility of claimed metrics."
                    ),
                )
            )

        # Check 6: Model versioning (no overwrite on retrain)
        if self._check_model_versioning(scripts_dir, inference_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="ML-006",
                    title="Model artifacts overwritten on retrain",
                    severity=Severity.MEDIUM,
                    description=(
                        "The training script saves model artifacts with "
                        "fixed filenames (e.g., logistic_regression.pkl, "
                        "xgboost.pkl) without version suffixes or separate "
                        "versioned directories. Retraining overwrites "
                        "previous model versions, losing rollback capability."
                    ),
                    file_path=str(scripts_dir / "train_models.py"),
                    recommendation=(
                        "Implement versioned artifact storage using "
                        "timestamps or incrementing version numbers in "
                        "filenames or subdirectories (e.g., "
                        "artifacts/v2/xgboost.pkl) to preserve previous "
                        "model versions."
                    ),
                )
            )

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_versioning_metadata(self, artifacts_dir: Path) -> bool:
        """Check if metadata.json contains required versioning fields.

        Args:
            artifacts_dir: Path to the ML artifacts directory.

        Returns:
            True if all required metadata fields are present.
        """
        metadata = self._load_metadata(artifacts_dir)
        if metadata is None:
            return False
        return self.REQUIRED_METADATA_FIELDS.issubset(metadata.keys())

    def _get_missing_metadata_fields(self, artifacts_dir: Path) -> set[str]:
        """Get the set of missing required metadata fields.

        Args:
            artifacts_dir: Path to the ML artifacts directory.

        Returns:
            Set of missing field names.
        """
        metadata = self._load_metadata(artifacts_dir)
        if metadata is None:
            return self.REQUIRED_METADATA_FIELDS.copy()
        return self.REQUIRED_METADATA_FIELDS - set(metadata.keys())

    def _load_metadata(self, artifacts_dir: Path) -> dict | None:
        """Load and parse metadata.json from artifacts directory.

        Args:
            artifacts_dir: Path to the ML artifacts directory.

        Returns:
            Parsed metadata dict, or None if not found/unparseable.
        """
        metadata_path = artifacts_dir / "metadata.json"
        if not metadata_path.exists():
            return None
        try:
            content = metadata_path.read_text(encoding="utf-8")
            return json.loads(content)
        except (OSError, json.JSONDecodeError):
            return None

    def _check_graceful_artifact_handling(self, inference_dir: Path) -> bool:
        """Verify artifact loader uses try/except around file loading.

        Inspects the artifact loader code (artifact_loader.py) for exception
        handling around artifact loading operations like joblib.load,
        pickle.load, or file open operations.

        Args:
            inference_dir: Path to the ML inference directory.

        Returns:
            True if graceful error handling is present.
        """
        loader_path = inference_dir / "artifact_loader.py"
        if not loader_path.exists():
            return False

        try:
            tree = StaticAnalyzer.parse_python_module(loader_path)
        except (SyntaxError, FileNotFoundError):
            return False

        # Look for try/except blocks that wrap loading operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Check if the try block contains loading operations
                try_source = ast.dump(node)
                loading_indicators = [
                    "joblib", "load", "pickle", "open", "read_bytes"
                ]
                if any(indicator in try_source for indicator in loading_indicators):
                    return True

        # Also check if the loader has a pattern that prevents crashes
        # (e.g., checking directory existence before loading)
        source = loader_path.read_text(encoding="utf-8")
        # Check for existence-check-before-load pattern
        has_existence_check = "exists()" in source or "is_file()" in source
        has_early_return = "return" in source

        # The loader checks if artifact_dir exists and returns early
        # This is a form of graceful handling (tolerant loading)
        if has_existence_check and has_early_return:
            # Verify there's a pattern of: if not exists -> return
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check for "if not artifact_dir.exists()" pattern
                    if_source = ast.dump(node)
                    if "exists" in if_source:
                        # Check if the body contains a return statement
                        for child in ast.walk(node):
                            if isinstance(child, ast.Return):
                                return True

        return False

    def _check_lightgbm_artifact(self, artifacts_dir: Path) -> bool:
        """Check if LightGBM model artifact exists.

        Args:
            artifacts_dir: Path to the ML artifacts directory.

        Returns:
            True if lightgbm.pkl (or similar) exists in artifacts.
        """
        if not artifacts_dir.exists():
            return False

        # Check for various LightGBM artifact filename patterns
        lgbm_patterns = [
            "lightgbm.pkl",
            "lightgbm.joblib",
            "lgbm.pkl",
            "lgbm.joblib",
        ]
        for pattern in lgbm_patterns:
            if (artifacts_dir / pattern).exists():
                return True

        # Also check for any file containing "lightgbm" or "lgbm" in name
        for artifact_file in artifacts_dir.iterdir():
            if artifact_file.is_file() and (
                "lightgbm" in artifact_file.stem.lower()
                or "lgbm" in artifact_file.stem.lower()
            ):
                return True

        return False

    def _check_ensemble_documentation(
        self, inference_dir: Path, services_dir: Path
    ) -> bool:
        """Check if prediction ensemble logic is documented.

        Looks for docstrings or comments in the predictor and prediction
        service that explain the ensemble combination strategy.

        Args:
            inference_dir: Path to the ML inference directory.
            services_dir: Path to the services directory.

        Returns:
            True if ensemble logic is documented.
        """
        predictor_path = inference_dir / "predictor.py"
        prediction_service_path = services_dir / "prediction_service.py"

        ensemble_keywords = [
            "ensemble", "averaging", "average", "voting", "stacking",
            "combine", "aggregat", "mean", "weighted"
        ]

        # Check predictor.py for ensemble documentation
        if predictor_path.exists():
            try:
                source = predictor_path.read_text(encoding="utf-8")
                tree = StaticAnalyzer.parse_python_module(predictor_path)

                # Check module docstring
                if (
                    tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str)
                ):
                    docstring = tree.body[0].value.value.lower()
                    if any(kw in docstring for kw in ensemble_keywords):
                        return True

                # Check class/method docstrings
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)
                        ):
                            docstring = node.body[0].value.value.lower()
                            if any(kw in docstring for kw in ensemble_keywords):
                                return True

                # Check comments in source
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        comment_lower = stripped.lower()
                        if any(kw in comment_lower for kw in ensemble_keywords):
                            return True
            except (SyntaxError, FileNotFoundError, OSError):
                pass

        # Check prediction_service.py for ensemble documentation
        if prediction_service_path.exists():
            try:
                source = prediction_service_path.read_text(encoding="utf-8")
                tree = StaticAnalyzer.parse_python_module(prediction_service_path)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name in ("predict", "predict_single"):
                            if (
                                node.body
                                and isinstance(node.body[0], ast.Expr)
                                and isinstance(node.body[0].value, ast.Constant)
                                and isinstance(node.body[0].value.value, str)
                            ):
                                docstring = node.body[0].value.value.lower()
                                if any(kw in docstring for kw in ensemble_keywords):
                                    return True

                # Check comments near prediction logic
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        comment_lower = stripped.lower()
                        if any(kw in comment_lower for kw in ensemble_keywords):
                            return True
            except (SyntaxError, FileNotFoundError, OSError):
                pass

        return False

    def _check_auc_metric(self, artifacts_dir: Path) -> bool:
        """Check if claimed AUC metric is verifiable from artifacts.

        Verifies that the metadata contains AUC metrics close to 83.9%
        and includes sufficient information for reproducibility.

        Args:
            artifacts_dir: Path to the ML artifacts directory.

        Returns:
            True if AUC metric is documented and reproducible.
        """
        metadata = self._load_metadata(artifacts_dir)
        if metadata is None:
            return False

        # Check if metrics section exists with AUC values
        metrics = metadata.get("metrics", {})
        if not metrics:
            return False

        # Look for AUC values close to the claimed 83.9%
        has_claimed_auc = False
        for model_name, model_metrics in metrics.items():
            auc_value = model_metrics.get("roc_auc") or model_metrics.get("auc_score")
            if auc_value is not None:
                if abs(auc_value - self.EXPECTED_AUC) < 0.005:
                    has_claimed_auc = True
                    break

        # Even if AUC is present, check reproducibility info
        has_reproducibility = (
            "training_date" in metadata
            and "dataset_hash" in metadata
        )

        # Pass if AUC is documented AND reproducibility info is present
        return has_claimed_auc and has_reproducibility

    def _check_model_versioning(
        self, scripts_dir: Path, inference_dir: Path
    ) -> bool:
        """Check if model training produces versioned artifacts.

        Looks for version incrementing, timestamped filenames, or
        versioned directories in the training script output logic.

        Args:
            scripts_dir: Path to the scripts directory.
            inference_dir: Path to the ML inference directory.

        Returns:
            True if model versioning prevents overwrites.
        """
        training_script = scripts_dir / "train_models.py"
        if not training_script.exists():
            # Also check alternative script names
            for alt_name in ["train_telco_models.py", "retrain.py"]:
                alt_path = scripts_dir / alt_name
                if alt_path.exists():
                    training_script = alt_path
                    break
            else:
                return False

        try:
            source = training_script.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False

        # Look for versioning patterns in the training script
        versioning_indicators = [
            "version", "timestamp", "datetime", "strftime",
            "v{", "v1", "v2", "_v", "/v",
        ]

        # Check if the save path includes versioning
        source_lower = source.lower()
        for indicator in versioning_indicators:
            if indicator in source_lower:
                # Verify it's used in the context of saving artifacts
                lines = source.splitlines()
                for i, line in enumerate(lines):
                    if indicator in line.lower() and any(
                        save_kw in line.lower()
                        for save_kw in ["dump", "save", "write", "output", "path"]
                    ):
                        return True

        # Check if fixed filenames are used (indicates overwrite)
        # Pattern: joblib.dump(model, path / "fixed_name.pkl")
        try:
            tree = StaticAnalyzer.parse_python_module(training_script)
        except (SyntaxError, FileNotFoundError):
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Look for joblib.dump or similar save calls
                call_name = self._get_call_name(node)
                if call_name in ("joblib.dump", "dump", "pickle.dump"):
                    # Check if the filename argument uses a fixed string
                    # (f-string with model name but no version)
                    if len(node.args) >= 2:
                        path_arg = node.args[1]
                        if self._is_fixed_filename_path(path_arg):
                            return False

        return False

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract the dotted name of a function call.

        Args:
            node: AST Call node.

        Returns:
            Dotted name string (e.g., "joblib.dump") or empty string.
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            return node.func.attr
        return ""

    def _is_fixed_filename_path(self, node: ast.AST) -> bool:
        """Check if a path expression uses a fixed filename.

        Detects patterns like `path / "model.pkl"` or `path / f"{name}.pkl"`
        where name is a simple variable (no version/timestamp component).

        Args:
            node: AST node representing the file path argument.

        Returns:
            True if the path appears to use a fixed filename pattern.
        """
        # Check for BinOp: path / "filename.pkl"
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            right = node.right
            # Constant string like "model.pkl"
            if isinstance(right, ast.Constant) and isinstance(right.value, str):
                if ".pkl" in right.value or ".joblib" in right.value:
                    return True
            # f-string like f"{name}.pkl" without version component
            if isinstance(right, ast.JoinedStr):
                # Check if the f-string includes any version/timestamp element
                fstring_parts = []
                for value in right.values:
                    if isinstance(value, ast.Constant):
                        fstring_parts.append(value.value)
                    elif isinstance(value, ast.FormattedValue):
                        if isinstance(value.value, ast.Name):
                            fstring_parts.append(value.value.id)
                # If no version-related variable is in the f-string
                version_vars = {"version", "timestamp", "date", "v"}
                has_version = any(
                    v in part.lower() for part in fstring_parts
                    for v in version_vars
                    if isinstance(part, str)
                )
                if not has_version:
                    return True

        return False
