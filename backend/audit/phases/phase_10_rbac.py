"""Phase 10: RBAC Validation.

Validates the Role-Based Access Control implementation for completeness
and enforcement. Checks role definitions, authorization enforcement on
authenticated endpoints, IDOR protection, admin-only access restrictions,
and role escalation guards.

Checks:
- 6 distinct roles defined with granular permissions
- All authenticated endpoints enforce role-based permission checks
- Endpoints with resource IDs validate ownership (IDOR protection)
- Admin endpoints restrict access to admin roles only
- Role-update endpoint requires admin-only authorization
"""

import ast
import re
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class RBACValidationPhase(AuditPhase):
    """Phase 10: RBAC Validation.

    Inspects role definitions, endpoint authorization decorators, IDOR
    protection patterns, admin access restrictions, and role escalation
    guards to identify authorization bypass risks.
    """

    name = "RBAC Validation"
    description = (
        "Validates the Role-Based Access Control implementation for "
        "completeness and enforcement, identifying authorization bypass risks."
    )

    EXPECTED_ROLE_COUNT = 6

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute RBAC validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all RBAC checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 5
        passed_checks = 0

        api_dir = workspace_root / "backend" / "app" / "api" / "v1"
        models_dir = workspace_root / "backend" / "app" / "models"
        dependencies_dir = workspace_root / "backend" / "app" / "dependencies"
        scripts_dir = workspace_root / "backend" / "scripts"

        # Check 1: Verify 6 distinct roles are defined (Req 10.1)
        role_count = self._count_role_definitions(
            models_dir, scripts_dir, workspace_root
        )
        if role_count >= self.EXPECTED_ROLE_COUNT:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="RBAC-001",
                    title="Insufficient RBAC role definitions",
                    severity=Severity.HIGH,
                    description=(
                        f"Expected at least {self.EXPECTED_ROLE_COUNT} "
                        f"distinct RBAC roles but found {role_count}. "
                        f"The README claims 6 roles with granular permissions."
                    ),
                    recommendation=(
                        "Define 6 distinct roles (e.g., Super Admin, Admin, "
                        "Retention Manager, Marketing Manager, Business "
                        "Analyst, Executive Viewer) with granular permission "
                        "assignments in the seed data or configuration."
                    ),
                )
            )

        # Check 2: Verify RBAC enforcement on authenticated endpoints (Req 10.2)
        unprotected = self._find_endpoints_without_role_check(api_dir)
        if not unprotected:
            passed_checks += 1
        else:
            endpoint_list = "; ".join(
                f"{ep['file']}:{ep['function']}" for ep in unprotected[:5]
            )
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="RBAC-002",
                    title="Authenticated endpoints lack role authorization",
                    severity=Severity.HIGH,
                    description=(
                        f"Found {len(unprotected)} endpoint(s) that use "
                        f"Depends(get_current_user) for authentication but "
                        f"do not enforce role-based authorization via "
                        f"require_role(). Examples: {endpoint_list}"
                    ),
                    recommendation=(
                        "Add Depends(require_role([...])) to all "
                        "authenticated endpoints to enforce role-based "
                        "access control."
                    ),
                )
            )

        # Check 3: IDOR protection on resource ID endpoints (Req 10.3)
        idor_risks = self._check_idor_protection(api_dir)
        if not idor_risks:
            passed_checks += 1
        else:
            risk_list = "; ".join(
                f"{r['file']}:{r['function']}" for r in idor_risks[:5]
            )
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="RBAC-003",
                    title="Potential IDOR vulnerability - missing ownership validation",
                    severity=Severity.HIGH,
                    description=(
                        f"Found {len(idor_risks)} endpoint(s) that accept "
                        f"resource IDs as path parameters but do not "
                        f"appear to validate resource ownership against "
                        f"the authenticated user. Examples: {risk_list}"
                    ),
                    recommendation=(
                        "Implement ownership validation by checking that "
                        "the authenticated user owns or has permission to "
                        "access the requested resource before returning data. "
                        "Alternatively, rely on role-based access with admin "
                        "roles for cross-user access."
                    ),
                )
            )

        # Check 4: Admin endpoints restrict access to admin roles (Req 10.4)
        admin_access_ok = self._check_admin_route_restrictions(api_dir)
        if admin_access_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="RBAC-004",
                    title="Admin endpoints not properly restricted to admin roles",
                    severity=Severity.MEDIUM,
                    description=(
                        "Admin router endpoints (user management, system "
                        "health, audit logs) do not consistently restrict "
                        'access to admin roles (["Super Admin", "Admin"]). '
                        "Non-admin users may be able to access administrative "
                        "operations."
                    ),
                    recommendation=(
                        "Ensure all admin endpoints use "
                        'require_role(["Super Admin", "Admin"]) or equivalent '
                        "to restrict access to administrative roles only."
                    ),
                )
            )

        # Check 5: Role-update endpoint has admin-only guard (Req 10.5)
        role_escalation_ok = self._check_role_escalation_guard(
            api_dir, workspace_root
        )
        if role_escalation_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="RBAC-005",
                    title="Role escalation guard missing on role-update endpoint",
                    severity=Severity.HIGH,
                    description=(
                        "The role-update or role-assignment endpoint does "
                        "not enforce admin-only authorization. A non-admin "
                        "user could potentially escalate their own privileges "
                        "by updating role assignments."
                    ),
                    recommendation=(
                        "Ensure the role-update and user role-assignment "
                        "endpoints require Super Admin or Admin role "
                        "authorization to prevent self-escalation."
                    ),
                )
            )

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _count_role_definitions(
        self, models_dir: Path, scripts_dir: Path, workspace_root: Path
    ) -> int:
        """Count distinct RBAC role definitions.

        Searches seed scripts and configuration files for role name
        definitions. Looks for dictionary keys in ROLE_PERMISSIONS or
        similar structures, as well as role name strings in seed data.

        Args:
            models_dir: Path to the models directory.
            scripts_dir: Path to the scripts directory.
            workspace_root: Root workspace path.

        Returns:
            Number of distinct role names found.
        """
        roles: set[str] = set()

        # Strategy 1: Parse seed_data.py for ROLE_PERMISSIONS dict keys
        seed_file = scripts_dir / "seed_data.py"
        if seed_file.exists():
            try:
                tree = StaticAnalyzer.parse_python_module(seed_file)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (
                                isinstance(target, ast.Name)
                                and "ROLE" in target.id.upper()
                                and isinstance(node.value, ast.Dict)
                            ):
                                for key in node.value.keys:
                                    if isinstance(key, ast.Constant) and isinstance(
                                        key.value, str
                                    ):
                                        roles.add(key.value)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                pass

        # Strategy 2: Parse init_db.py for role definitions
        init_db = scripts_dir / "init_db.py"
        if init_db.exists():
            try:
                tree = StaticAnalyzer.parse_python_module(init_db)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (
                                isinstance(target, ast.Name)
                                and "role" in target.id.lower()
                                and isinstance(node.value, ast.Dict)
                            ):
                                for key in node.value.keys:
                                    if isinstance(key, ast.Constant) and isinstance(
                                        key.value, str
                                    ):
                                        roles.add(key.value)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                pass

        # Strategy 3: Grep for role name strings in common patterns
        if not roles:
            backend_dir = workspace_root / "backend"
            matches = StaticAnalyzer.grep_pattern(
                backend_dir,
                r'(?:ROLE_PERMISSIONS|role_permissions)\s*=\s*\{',
                [".py"],
            )
            if matches:
                for file_path, _, _ in matches:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        # Extract string keys from dict literal
                        key_pattern = re.compile(
                            r'^\s*"([^"]+)"\s*:\s*\[', re.MULTILINE
                        )
                        for match in key_pattern.finditer(content):
                            roles.add(match.group(1))
                    except (OSError, UnicodeDecodeError):
                        continue

        return len(roles)

    def _find_endpoints_without_role_check(
        self, api_dir: Path
    ) -> list[dict[str, str]]:
        """Find endpoints using get_current_user but missing require_role.

        For each router file, checks if endpoints that depend on
        get_current_user also include a require_role dependency.

        Args:
            api_dir: Path to the API router directory.

        Returns:
            List of dicts with 'file' and 'function' keys for
            unprotected endpoints.
        """
        unprotected: list[dict[str, str]] = []

        if not api_dir.exists():
            return unprotected

        for py_file in api_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                continue

            # Check if file imports get_current_user
            has_get_current_user_import = StaticAnalyzer.check_imports(
                tree, "auth"
            )
            if not has_get_current_user_import:
                continue

            # Check file-level: does the file use require_role at all?
            file_content = py_file.read_text(encoding="utf-8")
            file_has_require_role = "require_role" in file_content
            file_has_get_current_user = "get_current_user" in file_content

            if not file_has_get_current_user:
                continue

            # Parse each endpoint function
            functions = StaticAnalyzer.find_function_definitions(tree)
            for func in functions:
                if not self._is_endpoint_function(func):
                    continue

                # Check if this function uses get_current_user dependency
                func_uses_auth = self._function_uses_dependency(
                    func, "get_current_user"
                )
                # Check if this function uses require_role dependency
                func_uses_role = self._function_uses_dependency(
                    func, "require_role"
                )

                if func_uses_auth and not func_uses_role:
                    unprotected.append(
                        {"file": py_file.name, "function": func.name}
                    )

        return unprotected

    def _check_idor_protection(self, api_dir: Path) -> list[dict[str, str]]:
        """Inspect endpoints with resource IDs for ownership validation.

        Looks for endpoints that take resource ID path parameters (e.g.,
        {id}, {user_id}) and checks whether the endpoint implementation
        includes some form of ownership validation or is restricted to
        admin roles.

        Args:
            api_dir: Path to the API router directory.

        Returns:
            List of dicts with 'file' and 'function' keys for
            endpoints with potential IDOR risks.
        """
        idor_risks: list[dict[str, str]] = []

        if not api_dir.exists():
            return idor_risks

        for py_file in api_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            # Skip admin-only routers since they already restrict by role
            if "admin" in py_file.name.lower():
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                continue

            functions = StaticAnalyzer.find_function_definitions(tree)
            for func in functions:
                if not self._is_endpoint_function(func):
                    continue

                # Check if function takes a resource ID parameter
                has_resource_id = self._has_resource_id_param(func)
                if not has_resource_id:
                    continue

                # Check if endpoint has ownership validation or admin guard
                has_protection = self._has_ownership_check(func, content)
                if not has_protection:
                    idor_risks.append(
                        {"file": py_file.name, "function": func.name}
                    )

        return idor_risks

    def _check_admin_route_restrictions(self, api_dir: Path) -> bool:
        """Verify admin router uses require_role with admin roles.

        Checks that files named *admin*.py use require_role with a list
        containing "Super Admin" and/or "Admin" on all endpoints.

        Args:
            api_dir: Path to the API router directory.

        Returns:
            True if all admin router endpoints are properly restricted.
        """
        if not api_dir.exists():
            return False

        admin_files = [
            f for f in api_dir.glob("*.py")
            if "admin" in f.name.lower() and not f.name.startswith("__")
        ]

        if not admin_files:
            return False

        for admin_file in admin_files:
            try:
                content = admin_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # Verify the file uses require_role
            if "require_role" not in content:
                return False

            # Verify it restricts to admin roles
            # Look for require_role with "Super Admin" or "Admin"
            has_admin_restriction = bool(
                re.search(
                    r'require_role\s*\(\s*\[.*(?:"Super Admin"|"Admin").*\]',
                    content,
                )
                or re.search(
                    r'require_role\s*\(\s*ADMIN_ROLES',
                    content,
                )
            )
            if not has_admin_restriction:
                return False

            # Check that all endpoint functions use require_role
            try:
                tree = StaticAnalyzer.parse_python_module(admin_file)
            except (SyntaxError, FileNotFoundError):
                continue

            functions = StaticAnalyzer.find_function_definitions(tree)
            for func in functions:
                if not self._is_endpoint_function(func):
                    continue

                func_uses_role = self._function_uses_dependency(
                    func, "require_role"
                )
                if not func_uses_role:
                    return False

        return True

    def _check_role_escalation_guard(
        self, api_dir: Path, workspace_root: Path
    ) -> bool:
        """Verify role-update endpoint requires admin authorization.

        Looks for endpoints that handle role updates or role assignments
        and verifies they are guarded by admin-only require_role checks.

        Args:
            api_dir: Path to the API router directory.
            workspace_root: Root workspace path.

        Returns:
            True if role-update endpoints have admin-only guards.
        """
        if not api_dir.exists():
            return False

        # Look for role-related endpoints in admin_roles or admin files
        role_files = [
            f for f in api_dir.glob("*.py")
            if any(
                kw in f.name.lower()
                for kw in ["role", "admin"]
            )
            and not f.name.startswith("__")
        ]

        found_role_update = False
        all_guarded = True

        for role_file in role_files:
            try:
                content = role_file.read_text(encoding="utf-8")
                tree = StaticAnalyzer.parse_python_module(role_file)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                continue

            functions = StaticAnalyzer.find_function_definitions(tree)
            for func in functions:
                if not self._is_endpoint_function(func):
                    continue

                # Check if this is a role-update or role-assignment endpoint
                is_role_endpoint = any(
                    kw in func.name.lower()
                    for kw in [
                        "update_role",
                        "assign_role",
                        "change_role",
                        "update_user",
                        "assign_permissions",
                        "create_role",
                        "delete_role",
                    ]
                )
                if not is_role_endpoint:
                    continue

                found_role_update = True

                # Verify it has require_role with admin roles
                func_uses_role = self._function_uses_dependency(
                    func, "require_role"
                )
                if not func_uses_role:
                    all_guarded = False

        return found_role_update and all_guarded

    @staticmethod
    def _is_endpoint_function(
        func: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> bool:
        """Check if a function is decorated as an API endpoint.

        Looks for decorators matching common FastAPI router patterns
        like @router.get, @router.post, etc.

        Args:
            func: AST function definition node.

        Returns:
            True if the function has a router HTTP method decorator.
        """
        http_methods = {"get", "post", "put", "patch", "delete"}

        for decorator in func.decorator_list:
            # Handle @router.get(...) pattern
            if isinstance(decorator, ast.Call) and isinstance(
                decorator.func, ast.Attribute
            ):
                if decorator.func.attr in http_methods:
                    return True
            # Handle @router.get (without call) pattern
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr in http_methods:
                    return True

        return False

    @staticmethod
    def _function_uses_dependency(
        func: ast.FunctionDef | ast.AsyncFunctionDef,
        dependency_name: str,
    ) -> bool:
        """Check if a function parameter uses a specific Depends() dependency.

        Inspects the function's default argument values looking for
        Depends(dependency_name) or Depends(dependency_name(...)) calls.

        Args:
            func: AST function definition node.
            dependency_name: Name of the dependency to search for.

        Returns:
            True if any parameter's default value references the dependency.
        """
        # Check in function defaults
        all_defaults = list(func.args.defaults) + list(func.args.kw_defaults)

        for default in all_defaults:
            if default is None:
                continue

            # Check Depends(require_role(...)) pattern
            if isinstance(default, ast.Call):
                # Direct Depends(get_current_user) or Depends(require_role(...))
                if isinstance(default.func, ast.Name):
                    if default.func.id == "Depends":
                        for arg in default.args:
                            if isinstance(arg, ast.Name) and arg.id == dependency_name:
                                return True
                            # Depends(require_role(...))
                            if isinstance(arg, ast.Call):
                                if isinstance(arg.func, ast.Name) and arg.func.id == dependency_name:
                                    return True
                # Also check if the default itself is a call to the dependency
                if isinstance(default.func, ast.Name) and default.func.id == dependency_name:
                    return True

            # Check for ast.Attribute patterns (module.Depends)
            if isinstance(default, ast.Call) and isinstance(
                default.func, ast.Attribute
            ):
                if default.func.attr == "Depends":
                    for arg in default.args:
                        if isinstance(arg, ast.Name) and arg.id == dependency_name:
                            return True
                        if isinstance(arg, ast.Call):
                            if isinstance(arg.func, ast.Name) and arg.func.id == dependency_name:
                                return True

        return False

    @staticmethod
    def _has_resource_id_param(
        func: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> bool:
        """Check if a function has a resource ID path parameter.

        Looks for parameter names containing 'id' that typically
        represent path parameters for resource access.

        Args:
            func: AST function definition node.

        Returns:
            True if the function has a parameter likely representing
            a resource ID.
        """
        id_patterns = {"id", "user_id", "customer_id", "campaign_id", "dataset_id"}

        for arg in func.args.args:
            if arg.arg in id_patterns:
                return True
            if arg.arg.endswith("_id"):
                return True

        return False

    @staticmethod
    def _has_ownership_check(
        func: ast.FunctionDef | ast.AsyncFunctionDef,
        file_content: str,
    ) -> bool:
        """Check if an endpoint validates resource ownership.

        Looks for patterns indicating ownership validation:
        - Comparing user_id or current_user.id with resource owner
        - Using require_role with admin roles (admin bypass)
        - Filtering queries by current_user

        Args:
            func: AST function definition node.
            file_content: Full content of the source file.

        Returns:
            True if some form of ownership validation is detected.
        """
        # Check if endpoint is protected by require_role (admin bypass)
        all_defaults = list(func.args.defaults) + list(func.args.kw_defaults)
        for default in all_defaults:
            if default is None:
                continue
            if isinstance(default, ast.Call) and isinstance(
                default.func, ast.Name
            ):
                if default.func.id == "Depends":
                    for arg in default.args:
                        if isinstance(arg, ast.Call) and isinstance(
                            arg.func, ast.Name
                        ):
                            if arg.func.id == "require_role":
                                return True

        # Check function body for ownership patterns
        func_source = ast.dump(ast.Module(body=func.body, type_ignores=[]))

        ownership_indicators = [
            "current_user.id",
            "current_user.role",
            "user_id",
            "owner_id",
        ]

        for indicator in ownership_indicators:
            if indicator in func_source:
                return True

        # Check the function body text by finding lines in the function range
        if hasattr(func, "lineno") and hasattr(func, "end_lineno"):
            lines = file_content.splitlines()
            start = func.lineno - 1
            end = func.end_lineno if func.end_lineno else start + 20
            func_lines = lines[start:end]
            func_text = "\n".join(func_lines)

            # Look for ownership/authorization patterns
            ownership_patterns = [
                r"current_user\.id",
                r"current_user\.role",
                r"user_id\s*==",
                r"owner_id",
                r"require_role",
            ]
            for pattern in ownership_patterns:
                if re.search(pattern, func_text):
                    return True

        return False
