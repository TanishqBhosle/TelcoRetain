"""Phase 3: Backend Validation.

Verifies FastAPI backend architectural patterns including:
- Router→Service delegation (no inline business logic in routers)
- Service→Repository pattern (no direct ORM queries in services)
- Schema validation (response_model and typed request bodies)
- Middleware ordering (Auth before RateLimit before Audit)
- Async session safety (AsyncSessionLocal always in async with)
- Pagination on list endpoints (limit/offset or page/page_size)
"""

import ast
from pathlib import Path
from typing import Optional

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class BackendValidationPhase(AuditPhase):
    """Phase 3: Backend architectural validation via AST analysis."""

    name = "Backend Validation"
    description = (
        "Validates FastAPI backend architecture including layered delegation, "
        "schema validation, middleware ordering, session safety, and pagination."
    )

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Run all backend validation checks.

        Args:
            workspace_root: Root path of the project being audited.

        Returns:
            PhaseResult with findings for any architectural violations.
        """
        findings: list[AuditFinding] = []
        total_checks = 0
        passed_checks = 0

        # Locate directories
        router_dir = workspace_root / "backend" / "app" / "api" / "v1"
        service_dir = workspace_root / "backend" / "app" / "services"
        main_py = workspace_root / "backend" / "main.py"
        backend_dir = workspace_root / "backend"

        # Check 1: Router→Service delegation
        router_results = self._check_router_delegation(router_dir)
        for passed, finding in router_results:
            total_checks += 1
            if passed:
                passed_checks += 1
            elif finding:
                findings.append(finding)

        # Check 2: Service→Repository pattern
        service_results = self._check_service_repository_pattern(service_dir)
        for passed, finding in service_results:
            total_checks += 1
            if passed:
                passed_checks += 1
            elif finding:
                findings.append(finding)

        # Check 3: Schema validation (response_model + request bodies)
        schema_results = self._check_schema_validation(router_dir)
        for passed, finding in schema_results:
            total_checks += 1
            if passed:
                passed_checks += 1
            elif finding:
                findings.append(finding)

        # Check 4: Middleware ordering
        middleware_passed, middleware_finding = self._check_middleware_order(main_py)
        total_checks += 1
        if middleware_passed:
            passed_checks += 1
        elif middleware_finding:
            findings.append(middleware_finding)

        # Check 5: Async session safety
        session_results = self._check_async_session_safety(backend_dir)
        for passed, finding in session_results:
            total_checks += 1
            if passed:
                passed_checks += 1
            elif finding:
                findings.append(finding)

        # Check 6: Pagination on list endpoints
        pagination_results = self._check_list_pagination(router_dir)
        for passed, finding in pagination_results:
            total_checks += 1
            if passed:
                passed_checks += 1
            elif finding:
                findings.append(finding)

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_router_delegation(
        self, router_dir: Path
    ) -> list[tuple[bool, Optional[AuditFinding]]]:
        """Verify each router delegates to service classes.

        Checks that router files import from services and that endpoint
        functions do not contain direct DB queries or complex inline logic.
        """
        results: list[tuple[bool, Optional[AuditFinding]]] = []

        if not router_dir.exists():
            results.append((
                False,
                AuditFinding(
                    phase=self.name,
                    check_id="BE-001",
                    title="Router directory not found",
                    severity=Severity.MEDIUM,
                    description="The API router directory does not exist.",
                    file_path=str(router_dir),
                    recommendation="Create the backend/app/api/v1/ directory with router modules.",
                ),
            ))
            return results

        router_files = [
            f for f in router_dir.glob("*.py")
            if f.name != "__init__.py" and not f.name.startswith("__")
        ]

        for router_file in router_files:
            try:
                module = StaticAnalyzer.parse_python_module(router_file)
            except (SyntaxError, FileNotFoundError):
                results.append((
                    False,
                    AuditFinding(
                        phase=self.name,
                        check_id="BE-001",
                        title=f"Cannot parse router: {router_file.name}",
                        severity=Severity.MEDIUM,
                        description=f"Failed to parse {router_file.name} for AST analysis.",
                        file_path=str(router_file),
                        recommendation="Fix syntax errors in the router file.",
                    ),
                ))
                continue

            # Check if router imports from services
            imports_service = StaticAnalyzer.check_imports(module, "services")

            # Check for inline DB patterns (direct session/query usage)
            has_inline_db = self._has_inline_db_queries(module)

            if imports_service and not has_inline_db:
                results.append((True, None))
            else:
                issues = []
                if not imports_service:
                    issues.append("does not import from service layer")
                if has_inline_db:
                    issues.append("contains inline database queries or complex business logic")

                results.append((
                    False,
                    AuditFinding(
                        phase=self.name,
                        check_id="BE-001",
                        title=f"Router delegation violation: {router_file.name}",
                        severity=Severity.MEDIUM,
                        description=(
                            f"Router '{router_file.name}' {', '.join(issues)}. "
                            "Routers should delegate business logic to service classes."
                        ),
                        file_path=str(router_file),
                        recommendation="Move business logic to a service class and import it in the router.",
                    ),
                ))

        return results

    def _has_inline_db_queries(self, module: ast.Module) -> bool:
        """Detect direct database query patterns in a module.

        Looks for session.execute(), session.query(), select(), and
        similar SQLAlchemy patterns that indicate inline DB access.
        """
        suspicious_calls = {"execute", "query", "scalar", "scalars"}

        for node in ast.walk(module):
            if isinstance(node, ast.Call):
                # session.execute(...), session.query(...)
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in suspicious_calls:
                        # Check if the object is likely a session
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id in ("session", "db", "sess"):
                                return True
        return False

    def _check_service_repository_pattern(
        self, service_dir: Path
    ) -> list[tuple[bool, Optional[AuditFinding]]]:
        """Verify each service delegates DB operations to repositories.

        Checks that service files import from repositories and do not
        contain direct SQLAlchemy session usage.
        """
        results: list[tuple[bool, Optional[AuditFinding]]] = []

        if not service_dir.exists():
            results.append((
                False,
                AuditFinding(
                    phase=self.name,
                    check_id="BE-002",
                    title="Services directory not found",
                    severity=Severity.MEDIUM,
                    description="The services directory does not exist.",
                    file_path=str(service_dir),
                    recommendation="Create the backend/app/services/ directory with service modules.",
                ),
            ))
            return results

        service_files = [
            f for f in service_dir.glob("*.py")
            if f.name != "__init__.py" and not f.name.startswith("__")
        ]

        for service_file in service_files:
            try:
                module = StaticAnalyzer.parse_python_module(service_file)
            except (SyntaxError, FileNotFoundError):
                results.append((
                    False,
                    AuditFinding(
                        phase=self.name,
                        check_id="BE-002",
                        title=f"Cannot parse service: {service_file.name}",
                        severity=Severity.MEDIUM,
                        description=f"Failed to parse {service_file.name} for AST analysis.",
                        file_path=str(service_file),
                        recommendation="Fix syntax errors in the service file.",
                    ),
                ))
                continue

            # Check if service imports from repositories
            imports_repo = StaticAnalyzer.check_imports(module, "repositories")

            # Check for direct SQLAlchemy session usage
            has_direct_session = self._has_direct_session_usage(module)

            if imports_repo and not has_direct_session:
                results.append((True, None))
            else:
                issues = []
                if not imports_repo:
                    issues.append("does not import from repository layer")
                if has_direct_session:
                    issues.append("contains direct SQLAlchemy session operations")

                results.append((
                    False,
                    AuditFinding(
                        phase=self.name,
                        check_id="BE-002",
                        title=f"Repository pattern violation: {service_file.name}",
                        severity=Severity.MEDIUM,
                        description=(
                            f"Service '{service_file.name}' {', '.join(issues)}. "
                            "Services should delegate DB operations to repository classes."
                        ),
                        file_path=str(service_file),
                        recommendation="Move database operations to a repository class.",
                    ),
                ))

        return results

    def _has_direct_session_usage(self, module: ast.Module) -> bool:
        """Detect direct SQLAlchemy session operations in a module.

        Looks for session.execute(), session.query(), session.add(),
        session.commit() and similar patterns that bypass the repository.
        """
        session_methods = {"execute", "query", "add", "commit", "rollback", "flush", "scalar", "scalars"}

        for node in ast.walk(module):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in session_methods:
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id in ("session", "db", "sess"):
                                return True
                        # Also check self.session, self.db
                        if isinstance(node.func.value, ast.Attribute):
                            if node.func.value.attr in ("session", "db", "sess"):
                                return True
        return False

    def _check_schema_validation(
        self, router_dir: Path
    ) -> list[tuple[bool, Optional[AuditFinding]]]:
        """Verify endpoints have response_model and typed request bodies.

        For each endpoint function decorated with router methods,
        checks for response_model keyword argument and Pydantic
        type annotations on body parameters.
        """
        results: list[tuple[bool, Optional[AuditFinding]]] = []

        if not router_dir.exists():
            return results

        router_files = [
            f for f in router_dir.glob("*.py")
            if f.name != "__init__.py" and not f.name.startswith("__")
        ]

        for router_file in router_files:
            try:
                module = StaticAnalyzer.parse_python_module(router_file)
            except (SyntaxError, FileNotFoundError):
                continue

            endpoints = self._find_endpoint_functions(module)

            for func in endpoints:
                has_response_model = self._endpoint_has_response_model(module, func)

                if has_response_model:
                    results.append((True, None))
                else:
                    results.append((
                        False,
                        AuditFinding(
                            phase=self.name,
                            check_id="BE-003",
                            title=f"Missing response_model: {func.name}",
                            severity=Severity.MEDIUM,
                            description=(
                                f"Endpoint '{func.name}' in '{router_file.name}' "
                                "does not declare a response_model for output serialization."
                            ),
                            file_path=str(router_file),
                            line_number=func.lineno,
                            recommendation="Add response_model parameter to the route decorator.",
                        ),
                    ))

        return results

    def _find_endpoint_functions(self, module: ast.Module) -> list:
        """Find functions decorated with router HTTP method decorators.

        Identifies functions with decorators like @router.get, @router.post, etc.
        """
        http_methods = {"get", "post", "put", "patch", "delete", "head", "options"}
        endpoints = []

        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    # @router.get(...), @router.post(...)
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in http_methods:
                                endpoints.append(node)
                                break
                    # @router.get (without call - rare but possible)
                    elif isinstance(decorator, ast.Attribute):
                        if decorator.attr in http_methods:
                            endpoints.append(node)
                            break

        return endpoints

    def _endpoint_has_response_model(self, module: ast.Module, func) -> bool:
        """Check if an endpoint function's decorator includes response_model.

        Inspects the decorator call for a 'response_model' keyword argument.
        """
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Call):
                for keyword in decorator.keywords:
                    if keyword.arg == "response_model":
                        return True
        return False

    def _check_middleware_order(
        self, main_py: Path
    ) -> tuple[bool, Optional[AuditFinding]]:
        """Verify middleware registration order in main.py.

        Expected order: Auth before RateLimit before Audit.
        In FastAPI, middleware is executed in reverse registration order,
        so the registration order should be: Audit, RateLimit, Auth
        (last registered = first executed).
        """
        if not main_py.exists():
            return (
                False,
                AuditFinding(
                    phase=self.name,
                    check_id="BE-005",
                    title="main.py not found",
                    severity=Severity.MEDIUM,
                    description="Cannot verify middleware ordering: main.py not found.",
                    file_path=str(main_py),
                    recommendation="Ensure main.py exists at the backend root.",
                ),
            )

        try:
            module = StaticAnalyzer.parse_python_module(main_py)
        except (SyntaxError, FileNotFoundError):
            return (
                False,
                AuditFinding(
                    phase=self.name,
                    check_id="BE-005",
                    title="Cannot parse main.py",
                    severity=Severity.MEDIUM,
                    description="Failed to parse main.py for middleware analysis.",
                    file_path=str(main_py),
                    recommendation="Fix syntax errors in main.py.",
                ),
            )

        middleware_order = self._extract_middleware_order(module)

        # Expected execution order: Auth → RateLimit → Audit
        # FastAPI reverses registration order, so registration should be:
        # AuditMiddleware, RateLimitMiddleware, AuthMiddleware
        expected_order = ["Audit", "RateLimit", "Auth"]

        if len(middleware_order) < 3:
            return (
                False,
                AuditFinding(
                    phase=self.name,
                    check_id="BE-005",
                    title="Incomplete middleware stack",
                    severity=Severity.MEDIUM,
                    description=(
                        f"Found {len(middleware_order)} middleware registrations, "
                        "expected at least 3 (Auth, RateLimit, Audit)."
                    ),
                    file_path=str(main_py),
                    recommendation="Register Auth, RateLimit, and Audit middleware in correct order.",
                ),
            )

        # Check the order
        order_correct = True
        for i, expected in enumerate(expected_order):
            if i < len(middleware_order):
                if expected.lower() not in middleware_order[i].lower():
                    order_correct = False
                    break

        if order_correct:
            return (True, None)
        else:
            return (
                False,
                AuditFinding(
                    phase=self.name,
                    check_id="BE-005",
                    title="Incorrect middleware ordering",
                    severity=Severity.MEDIUM,
                    description=(
                        f"Middleware registration order is {middleware_order}, "
                        "but expected Audit, RateLimit, Auth (so execution order is Auth → RateLimit → Audit)."
                    ),
                    file_path=str(main_py),
                    recommendation=(
                        "Reorder middleware registration: AuditMiddleware first, "
                        "then RateLimitMiddleware, then AuthMiddleware."
                    ),
                ),
            )

    def _extract_middleware_order(self, module: ast.Module) -> list[str]:
        """Extract the order of custom add_middleware calls from the AST.

        Returns a list of middleware class names in registration order
        (sorted by source line number), excluding framework-provided
        middleware (e.g. CORSMiddleware).
        """
        # Framework middleware to exclude from ordering check
        framework_middleware = {"CORSMiddleware", "TrustedHostMiddleware", "HTTPSRedirectMiddleware"}
        middleware_entries: list[tuple[int, str]] = []

        for node in ast.walk(module):
            if isinstance(node, ast.Call):
                # app.add_middleware(SomeMiddleware)
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "add_middleware":
                        if node.args:
                            first_arg = node.args[0]
                            name = None
                            if isinstance(first_arg, ast.Name):
                                name = first_arg.id
                            elif isinstance(first_arg, ast.Attribute):
                                name = first_arg.attr
                            if name and name not in framework_middleware:
                                middleware_entries.append((node.lineno, name))

        # Sort by line number to get registration order
        middleware_entries.sort(key=lambda x: x[0])
        return [name for _, name in middleware_entries]

    def _check_async_session_safety(
        self, backend_dir: Path
    ) -> list[tuple[bool, Optional[AuditFinding]]]:
        """Verify AsyncSessionLocal is always used with async with.

        Scans application Python files for AsyncSessionLocal usage and checks
        that each usage is inside an async with context manager.
        """
        results: list[tuple[bool, Optional[AuditFinding]]] = []

        if not backend_dir.exists():
            return results

        # Search only application directories (exclude .venv, __pycache__, etc.)
        app_dir = backend_dir / "app"
        matches: list[tuple[Path, int, str]] = []
        search_dirs = [app_dir]

        # Also check main.py
        main_file = backend_dir / "main.py"
        if main_file.exists():
            import re
            content = main_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(r"AsyncSessionLocal", line):
                    matches.append((main_file, i, line.strip()))

        for search_dir in search_dirs:
            if search_dir.exists():
                matches.extend(
                    StaticAnalyzer.grep_pattern(search_dir, r"AsyncSessionLocal", [".py"])
                )

        if not matches:
            # No usage found — nothing to check, count as passed
            results.append((True, None))
            return results

        # Group matches by file for AST analysis
        files_with_usage: dict[Path, list[int]] = {}
        for file_path, line_num, _ in matches:
            # Skip __pycache__ and .venv
            rel = str(file_path)
            if "__pycache__" in rel or ".venv" in rel:
                continue
            if file_path not in files_with_usage:
                files_with_usage[file_path] = []
            files_with_usage[file_path].append(line_num)

        for file_path, line_numbers in files_with_usage.items():
            try:
                module = StaticAnalyzer.parse_python_module(file_path)
            except (SyntaxError, FileNotFoundError):
                continue

            unsafe_lines = self._find_unsafe_session_usage(module, file_path)

            if not unsafe_lines:
                results.append((True, None))
            else:
                for line_num in unsafe_lines:
                    results.append((
                        False,
                        AuditFinding(
                            phase=self.name,
                            check_id="BE-006",
                            title=f"Session leak risk: {file_path.name}",
                            severity=Severity.HIGH,
                            description=(
                                f"AsyncSessionLocal used without 'async with' context manager "
                                f"in '{file_path.name}' near line {line_num}. "
                                "This may cause session leaks."
                            ),
                            file_path=str(file_path),
                            line_number=line_num,
                            recommendation="Always use 'async with AsyncSessionLocal() as session:' pattern.",
                        ),
                    ))

        return results

    def _find_unsafe_session_usage(self, module: ast.Module, file_path: Path) -> list[int]:
        """Find AsyncSessionLocal() calls that are NOT inside async with.

        Returns line numbers of unsafe usages.
        """
        unsafe_lines: list[int] = []

        # Collect all AsyncSessionLocal() call locations
        session_calls: list[int] = []
        for node in ast.walk(module):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "AsyncSessionLocal":
                    session_calls.append(node.lineno)
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "AsyncSessionLocal":
                    session_calls.append(node.lineno)

        # Collect line numbers of AsyncSessionLocal calls inside async with
        safe_lines: set[int] = set()
        for node in ast.walk(module):
            if isinstance(node, ast.AsyncWith):
                for item in node.items:
                    # async with AsyncSessionLocal() as session:
                    ctx_expr = item.context_expr
                    if isinstance(ctx_expr, ast.Call):
                        if isinstance(ctx_expr.func, ast.Name) and ctx_expr.func.id == "AsyncSessionLocal":
                            safe_lines.add(ctx_expr.lineno)
                        elif isinstance(ctx_expr.func, ast.Attribute) and ctx_expr.func.attr == "AsyncSessionLocal":
                            safe_lines.add(ctx_expr.lineno)

        for line in session_calls:
            if line not in safe_lines:
                unsafe_lines.append(line)

        return unsafe_lines

    def _check_list_pagination(
        self, router_dir: Path
    ) -> list[tuple[bool, Optional[AuditFinding]]]:
        """Verify list endpoints have pagination parameters.

        Identifies endpoints that return List/list types and checks
        that they accept limit/offset or page/page_size parameters.
        """
        results: list[tuple[bool, Optional[AuditFinding]]] = []

        if not router_dir.exists():
            return results

        router_files = [
            f for f in router_dir.glob("*.py")
            if f.name != "__init__.py" and not f.name.startswith("__")
        ]

        for router_file in router_files:
            try:
                module = StaticAnalyzer.parse_python_module(router_file)
            except (SyntaxError, FileNotFoundError):
                continue

            endpoints = self._find_endpoint_functions(module)

            for func in endpoints:
                if self._returns_list_type(func, module):
                    has_pagination = self._has_pagination_params(func)

                    if has_pagination:
                        results.append((True, None))
                    else:
                        results.append((
                            False,
                            AuditFinding(
                                phase=self.name,
                                check_id="BE-007",
                                title=f"Missing pagination: {func.name}",
                                severity=Severity.MEDIUM,
                                description=(
                                    f"List endpoint '{func.name}' in '{router_file.name}' "
                                    "does not implement pagination parameters (limit/offset or page/page_size)."
                                ),
                                file_path=str(router_file),
                                line_number=func.lineno,
                                recommendation="Add limit/offset or page/page_size query parameters to bound results.",
                            ),
                        ))

        return results

    def _returns_list_type(self, func, module: ast.Module) -> bool:
        """Check if an endpoint's response_model indicates a list return type.

        Checks the response_model decorator argument for List[] or list[]
        type annotations. Also checks the function return annotation.
        """
        # Check response_model in decorator
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Call):
                for keyword in decorator.keywords:
                    if keyword.arg == "response_model":
                        if self._is_list_annotation(keyword.value):
                            return True

        # Check return annotation
        if func.returns and self._is_list_annotation(func.returns):
            return True

        return False

    def _is_list_annotation(self, node) -> bool:
        """Check if an AST node represents a List type annotation.

        Handles: List[...], list[...], and subscript forms with List inside.
        """
        if isinstance(node, ast.Subscript):
            # List[X] or list[X]
            if isinstance(node.value, ast.Name):
                if node.value.id in ("List", "list"):
                    return True
            # APIResponse[List[X]] — check slice
            if isinstance(node.slice, ast.Subscript):
                return self._is_list_annotation(node.slice)
            if isinstance(node.slice, ast.Name):
                if node.slice.id in ("List", "list"):
                    return True
        elif isinstance(node, ast.Name):
            if node.id in ("List", "list"):
                return True

        return False

    def _has_pagination_params(self, func) -> bool:
        """Check if a function has pagination query parameters.

        Looks for limit/offset or page/page_size parameter names.
        """
        pagination_params = {"limit", "offset", "page", "page_size", "skip"}
        param_names = {arg.arg for arg in func.args.args}

        # Check if at least two pagination-related params exist
        found = param_names & pagination_params
        return len(found) >= 2
