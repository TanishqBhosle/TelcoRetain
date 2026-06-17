"""Phase 1: Requirement Validation.

Validates that README-documented claims match the actual implementation
by counting routers, services, repositories, screens, tables, test files,
RBAC roles, and ML artifacts.
"""

import ast
import re
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


# README baseline claims
EXPECTED_ROUTERS = 11
EXPECTED_SERVICES = 12
EXPECTED_REPOSITORIES = 11
EXPECTED_SCREENS = 22
EXPECTED_TABLES = 22
EXPECTED_TEST_FILES = 15
EXPECTED_ROLES = 6
EXPECTED_ML_ARTIFACTS = ["xgboost", "lightgbm", "logistic_regression", "random_forest"]


class RequirementValidationPhase(AuditPhase):
    """Phase 1: Validates README claims against actual implementation.

    Checks counts of routers, services, repositories, screens, tables,
    test files, roles, and ML artifacts against documented baselines.
    """

    name = "Requirement Validation"
    description = (
        "Validates README-documented claims match the actual implementation "
        "to identify specification drift."
    )

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute requirement validation checks.

        Args:
            workspace_root: Path to the root of the TelcoRetain project.

        Returns:
            PhaseResult with findings for any discrepancies.
        """
        findings: list[AuditFinding] = []
        total_checks = 8
        passed_checks = 0

        # Check 1: API Routers (REQ-001)
        routers_dir = workspace_root / "backend" / "app" / "api" / "v1"
        router_count = self._count_python_modules(routers_dir)
        if router_count == EXPECTED_ROUTERS:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-001",
                title="Router count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_ROUTERS} API routers but found "
                    f"{router_count} in {routers_dir.relative_to(workspace_root)}."
                ),
                file_path=str(routers_dir.relative_to(workspace_root)),
                recommendation="Update README or add missing router modules.",
            ))

        # Check 2: Services (REQ-002)
        services_dir = workspace_root / "backend" / "app" / "services"
        service_count = self._count_python_modules(services_dir)
        if service_count == EXPECTED_SERVICES:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-002",
                title="Service count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_SERVICES} services but found "
                    f"{service_count} in {services_dir.relative_to(workspace_root)}."
                ),
                file_path=str(services_dir.relative_to(workspace_root)),
                recommendation="Update README or add missing service modules.",
            ))

        # Check 3: Repositories (REQ-003)
        repos_dir = workspace_root / "backend" / "app" / "repositories"
        repo_count = self._count_python_modules(repos_dir)
        if repo_count == EXPECTED_REPOSITORIES:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-003",
                title="Repository count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_REPOSITORIES} repositories but found "
                    f"{repo_count} in {repos_dir.relative_to(workspace_root)}."
                ),
                file_path=str(repos_dir.relative_to(workspace_root)),
                recommendation="Update README or add missing repository modules.",
            ))

        # Check 4: Screens (REQ-004)
        pages_dir = workspace_root / "frontend" / "src" / "pages"
        screen_count = StaticAnalyzer.count_files(pages_dir, "*.tsx")
        if screen_count == EXPECTED_SCREENS:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-004",
                title="Screen count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_SCREENS} screens but found "
                    f"{screen_count} in {pages_dir.relative_to(workspace_root)}."
                ),
                file_path=str(pages_dir.relative_to(workspace_root)),
                recommendation="Update README or add missing screen components.",
            ))

        # Check 5: Database Tables (REQ-005)
        models_dir = workspace_root / "backend" / "app" / "models"
        table_count = self._count_tablenames(models_dir)
        if table_count == EXPECTED_TABLES:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-005",
                title="Table count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_TABLES} tables but found "
                    f"{table_count} __tablename__ declarations in ORM models."
                ),
                file_path=str(models_dir.relative_to(workspace_root)),
                recommendation="Update README or add missing ORM model definitions.",
            ))

        # Check 6: Test Files (REQ-006)
        tests_dir = workspace_root / "backend" / "tests"
        test_count = StaticAnalyzer.count_files(tests_dir, "test_*.py")
        if test_count == EXPECTED_TEST_FILES:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-006",
                title="Test file count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_TEST_FILES} test files but found "
                    f"{test_count} in {tests_dir.relative_to(workspace_root)}."
                ),
                file_path=str(tests_dir.relative_to(workspace_root)),
                recommendation="Update README or add missing test files.",
            ))

        # Check 7: RBAC Roles (REQ-007)
        role_count = self._count_roles(workspace_root)
        if role_count == EXPECTED_ROLES:
            passed_checks += 1
        else:
            findings.append(AuditFinding(
                phase=self.name,
                check_id="REQ-007",
                title="RBAC role count mismatch",
                severity=Severity.MEDIUM,
                description=(
                    f"README claims {EXPECTED_ROLES} RBAC roles but found "
                    f"{role_count} role definitions."
                ),
                recommendation="Update README or adjust role definitions.",
            ))

        # Check 8: ML Artifacts (REQ-008)
        artifacts_dir = workspace_root / "backend" / "ml" / "artifacts"
        missing_artifacts = self._check_ml_artifacts(artifacts_dir)
        if not missing_artifacts:
            passed_checks += 1
        else:
            for artifact in missing_artifacts:
                findings.append(AuditFinding(
                    phase=self.name,
                    check_id="REQ-008",
                    title=f"Missing ML artifact: {artifact}",
                    severity=Severity.HIGH,
                    description=(
                        f"README claims {artifact} model artifact exists but "
                        f"no corresponding .pkl file was found in "
                        f"{artifacts_dir.relative_to(workspace_root)}."
                    ),
                    file_path=str(artifacts_dir.relative_to(workspace_root)),
                    recommendation=f"Train and export the {artifact} model artifact.",
                ))

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    @staticmethod
    def _count_python_modules(directory: Path) -> int:
        """Count Python files in a directory, excluding __init__.py.

        Args:
            directory: Directory to count .py files in.

        Returns:
            Number of .py files excluding __init__.py. Returns 0 if
            the directory does not exist.
        """
        if not directory.exists():
            return 0
        return len([
            f for f in directory.glob("*.py")
            if f.is_file() and f.name != "__init__.py"
        ])

    @staticmethod
    def _count_tablenames(models_dir: Path) -> int:
        """Count __tablename__ declarations in ORM model files.

        Parses each Python file in the models directory using AST and
        counts class-level assignments of __tablename__.

        Args:
            models_dir: Path to the models directory.

        Returns:
            Total number of __tablename__ declarations found.
        """
        if not models_dir.exists():
            return 0

        count = 0
        for py_file in models_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            try:
                module = StaticAnalyzer.parse_python_module(py_file)
                for node in StaticAnalyzer.find_class_definitions(module):
                    for item in node.body:
                        if (
                            isinstance(item, ast.Assign)
                            and any(
                                isinstance(t, ast.Name) and t.id == "__tablename__"
                                for t in item.targets
                            )
                        ):
                            count += 1
            except (SyntaxError, OSError):
                continue

        return count

    @staticmethod
    def _count_roles(workspace_root: Path) -> int:
        """Count RBAC role definitions from the seed data script.

        Looks for role definitions in the seed script by counting
        top-level keys in the ROLE_PERMISSIONS dictionary, or by
        searching for role name patterns in the codebase.

        Args:
            workspace_root: Path to the project root.

        Returns:
            Number of distinct roles found.
        """
        # Strategy: Search for role definitions in seed scripts or config
        seed_script = workspace_root / "backend" / "scripts" / "seed_data.py"
        if seed_script.exists():
            try:
                module = StaticAnalyzer.parse_python_module(seed_script)
                for node in ast.walk(module):
                    # Look for ROLE_PERMISSIONS dict assignment
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "ROLE_PERMISSIONS":
                                if isinstance(node.value, ast.Dict):
                                    return len(node.value.keys)
            except (SyntaxError, OSError):
                pass

        # Fallback: grep for role-like strings in the codebase
        matches = StaticAnalyzer.grep_pattern(
            workspace_root / "backend",
            r'^\s*["\'](?:Super Admin|Admin|Analyst|Manager|Viewer|Executive)',
            [".py"],
        )
        # Deduplicate role names found
        roles: set[str] = set()
        for _, _, line in matches:
            match = re.search(r'["\']([^"\']+)["\']', line)
            if match:
                roles.add(match.group(1))
        return len(roles)

    @staticmethod
    def _check_ml_artifacts(artifacts_dir: Path) -> list[str]:
        """Check for missing ML model .pkl artifacts.

        Args:
            artifacts_dir: Path to the ML artifacts directory.

        Returns:
            List of missing artifact names. Empty list if all present.
        """
        if not artifacts_dir.exists():
            return list(EXPECTED_ML_ARTIFACTS)

        missing: list[str] = []
        for artifact_name in EXPECTED_ML_ARTIFACTS:
            pkl_file = artifacts_dir / f"{artifact_name}.pkl"
            if not pkl_file.exists():
                missing.append(artifact_name)

        return missing
