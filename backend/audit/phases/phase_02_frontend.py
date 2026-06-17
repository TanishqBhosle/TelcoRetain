"""Phase 2: Frontend Validation.

Validates the frontend implementation for correctness, completeness,
and code quality by running TypeScript compilation checks, verifying
route definitions, authentication guards, localStorage security,
hardcoded secrets, and API client error handling.
"""

import asyncio
import re
import subprocess
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class FrontendValidationPhase(AuditPhase):
    """Phase 2: Frontend Validation.

    Checks:
    - TypeScript compilation (no type errors)
    - Route count matches documented 22 routes
    - Protected route wrappers on authenticated routes
    - Secure localStorage usage (no token persistence without expiration)
    - No hardcoded URLs, secrets, or credentials
    - API client error interceptors present
    """

    name = "Frontend Validation"
    description = (
        "Validates frontend implementation for TypeScript correctness, "
        "route coverage, authentication guards, and security practices."
    )

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute all frontend validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult containing check counts and any findings.
        """
        findings: list[AuditFinding] = []
        total_checks = 6
        passed_checks = 0

        frontend_dir = workspace_root / "frontend"
        src_dir = frontend_dir / "src"

        # Check 1: TypeScript compilation
        if self._check_typescript_compilation(frontend_dir, findings):
            passed_checks += 1

        # Check 2: Route count
        if self._check_route_count(src_dir, findings):
            passed_checks += 1

        # Check 3: Protected route wrappers
        if self._check_protected_routes(src_dir, findings):
            passed_checks += 1

        # Check 4: localStorage token security
        if self._check_local_storage_security(src_dir, findings):
            passed_checks += 1

        # Check 5: Hardcoded URLs/secrets/credentials
        if self._check_hardcoded_secrets(src_dir, findings):
            passed_checks += 1

        # Check 6: API client error interceptors
        if self._check_error_interceptors(src_dir, findings):
            passed_checks += 1

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_typescript_compilation(
        self, frontend_dir: Path, findings: list[AuditFinding]
    ) -> bool:
        """Run npx tsc --noEmit and parse output for TypeScript errors.

        Args:
            frontend_dir: Path to the frontend directory.
            findings: List to append any findings to.

        Returns:
            True if no TypeScript errors found, False otherwise.
        """
        if not frontend_dir.exists():
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-001",
                    title="Frontend directory not found",
                    severity=Severity.MEDIUM,
                    description=(
                        "The frontend directory does not exist at the expected path."
                    ),
                    recommendation="Ensure the frontend directory exists at the project root.",
                )
            )
            return False

        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=120,
                shell=True,
            )
        except FileNotFoundError:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-001",
                    title="TypeScript compiler not available",
                    severity=Severity.MEDIUM,
                    description=(
                        "npx or tsc is not available in the system PATH. "
                        "Unable to perform TypeScript type checking."
                    ),
                    recommendation=(
                        "Install Node.js and TypeScript globally or ensure "
                        "npx is available in the PATH."
                    ),
                )
            )
            return False
        except subprocess.TimeoutExpired:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-001",
                    title="TypeScript compilation timed out",
                    severity=Severity.MEDIUM,
                    description=(
                        "TypeScript compilation did not complete within 120 seconds."
                    ),
                    recommendation="Investigate compilation performance issues.",
                )
            )
            return False

        # Parse output for errors (tsc outputs errors to stdout)
        output = result.stdout + result.stderr
        error_pattern = re.compile(r"^(.+)\((\d+),(\d+)\):\s+error\s+TS\d+:", re.MULTILINE)
        errors = error_pattern.findall(output)

        if result.returncode != 0 and errors:
            error_count = len(errors)
            # Report up to 5 specific error locations
            sample_errors = errors[:5]
            error_details = "\n".join(
                f"  - {file}:{line}:{col}" for file, line, col in sample_errors
            )
            if error_count > 5:
                error_details += f"\n  ... and {error_count - 5} more errors"

            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-001",
                    title=f"TypeScript compilation errors ({error_count} errors)",
                    severity=Severity.MEDIUM,
                    description=(
                        f"TypeScript type checking found {error_count} errors:\n"
                        f"{error_details}"
                    ),
                    recommendation=(
                        "Fix TypeScript type errors to ensure type safety across "
                        "the frontend codebase."
                    ),
                )
            )
            return False

        return True

    def _check_route_count(
        self, src_dir: Path, findings: list[AuditFinding]
    ) -> bool:
        """Parse App.tsx for route definitions and count unique paths.

        Expects 22 unique route paths as documented.

        Args:
            src_dir: Path to the frontend src directory.
            findings: List to append any findings to.

        Returns:
            True if route count matches expected 22, False otherwise.
        """
        app_tsx = src_dir / "App.tsx"
        if not app_tsx.exists():
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-002",
                    title="App.tsx not found",
                    severity=Severity.MEDIUM,
                    description="Cannot locate App.tsx to verify route definitions.",
                    file_path=str(app_tsx),
                    recommendation="Ensure App.tsx exists in the frontend src directory.",
                )
            )
            return False

        content = app_tsx.read_text(encoding="utf-8")

        # Match <Route path="..." elements
        route_pattern = re.compile(r'<Route\s+[^>]*path=["\']([^"\']+)["\']')
        paths = route_pattern.findall(content)

        # Deduplicate paths
        unique_paths = set(paths)
        route_count = len(unique_paths)
        expected_count = 22

        if route_count < expected_count:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-002",
                    title=f"Route count mismatch ({route_count} found, {expected_count} expected)",
                    severity=Severity.MEDIUM,
                    description=(
                        f"Found {route_count} unique route paths in App.tsx, "
                        f"but README claims {expected_count} screens. "
                        f"Missing routes may indicate incomplete navigation."
                    ),
                    file_path=str(app_tsx),
                    recommendation=(
                        "Verify all documented screens have corresponding "
                        "route definitions in App.tsx."
                    ),
                )
            )
            return False

        return True

    def _check_protected_routes(
        self, src_dir: Path, findings: list[AuditFinding]
    ) -> bool:
        """Verify authenticated routes are wrapped in Protected or auth guard.

        Checks that routes requiring authentication use the <Protected>
        wrapper component or equivalent auth guard.

        Args:
            src_dir: Path to the frontend src directory.
            findings: List to append any findings to.

        Returns:
            True if protected routes are properly guarded, False otherwise.
        """
        app_tsx = src_dir / "App.tsx"
        if not app_tsx.exists():
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-003",
                    title="App.tsx not found for route protection check",
                    severity=Severity.HIGH,
                    description="Cannot locate App.tsx to verify route protection.",
                    file_path=str(app_tsx),
                    recommendation="Ensure App.tsx exists in the frontend src directory.",
                )
            )
            return False

        content = app_tsx.read_text(encoding="utf-8")

        # Check for Protected component definition or import
        has_protected = bool(
            re.search(r"function\s+Protected|<Protected\s*/?>\s*|<Protected\b", content)
        )

        if not has_protected:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-003",
                    title="Missing Protected route wrapper",
                    severity=Severity.HIGH,
                    description=(
                        "No <Protected> component found wrapping authenticated routes. "
                        "This means authenticated routes may be accessible without login."
                    ),
                    file_path=str(app_tsx),
                    recommendation=(
                        "Wrap authenticated route groups with a <Protected> component "
                        "that checks authentication state before rendering."
                    ),
                )
            )
            return False

        # Verify Protected component checks for token/auth state
        protected_def_match = re.search(
            r"function\s+Protected\s*\([^)]*\)\s*\{([\s\S]*?)\n\}",
            content,
        )
        if protected_def_match:
            protected_body = protected_def_match.group(1)
            checks_auth = bool(
                re.search(r"token|accessToken|isAuthenticated|auth", protected_body)
            )
            redirects_unauthenticated = bool(
                re.search(r"Navigate|redirect|navigate\(", protected_body)
            )

            if not checks_auth or not redirects_unauthenticated:
                findings.append(
                    AuditFinding(
                        phase=self.name,
                        check_id="FE-003",
                        title="Weak Protected route implementation",
                        severity=Severity.HIGH,
                        description=(
                            "Protected component does not adequately check "
                            "authentication state or redirect unauthenticated users."
                        ),
                        file_path=str(app_tsx),
                        recommendation=(
                            "Ensure Protected component checks for a valid token "
                            "and redirects to login if not authenticated."
                        ),
                    )
                )
                return False

        # Verify that admin/business routes are nested under Protected
        # Check that /admin and /app routes are within a <Route element={<Protected />}> block
        protected_block_pattern = re.compile(
            r'<Route\s+element=\{<Protected\s*/?\s*>\}[^>]*>([\s\S]*?)</Route>',
            re.MULTILINE,
        )
        protected_blocks = protected_block_pattern.findall(content)

        if not protected_blocks:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-003",
                    title="Authenticated routes not wrapped in Protected",
                    severity=Severity.HIGH,
                    description=(
                        "Could not confirm that authenticated routes (/admin, /app) "
                        "are nested within a Protected route wrapper."
                    ),
                    file_path=str(app_tsx),
                    recommendation=(
                        "Nest authenticated route groups under a layout route "
                        "with element={<Protected />}."
                    ),
                )
            )
            return False

        return True

    def _check_local_storage_security(
        self, src_dir: Path, findings: list[AuditFinding]
    ) -> bool:
        """Check for localStorage token persistence without expiration.

        Tokens stored in localStorage without expiration mechanisms are
        vulnerable to theft via XSS and never expire client-side.

        Args:
            src_dir: Path to the frontend src directory.
            findings: List to append any findings to.

        Returns:
            True if no insecure localStorage usage found, False otherwise.
        """
        # Search for localStorage.setItem with token-related keys
        matches = StaticAnalyzer.grep_pattern(
            src_dir,
            r'localStorage\.(setItem|getItem)\s*\(\s*["\'].*[Tt]oken',
            [".ts", ".tsx"],
        )

        if not matches:
            return True

        # Check if there's an expiration mechanism alongside token storage
        has_expiry = False
        for file_path, _, _ in matches:
            try:
                file_content = file_path.read_text(encoding="utf-8")
                # Look for expiration-related logic near token storage
                if re.search(
                    r"expir|ttl|maxAge|max_age|tokenExpiry|expiresAt|setTimeout.*remove",
                    file_content,
                    re.IGNORECASE,
                ):
                    has_expiry = True
                    break
            except (OSError, UnicodeDecodeError):
                continue

        if not has_expiry:
            sample_locations = [
                f"  - {path.relative_to(src_dir.parent.parent)}:{line}"
                for path, line, _ in matches[:3]
            ]
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-004",
                    title="localStorage token persistence without expiration",
                    severity=Severity.MEDIUM,
                    description=(
                        "Tokens are stored in localStorage without client-side "
                        "expiration mechanisms. Tokens persisted in localStorage "
                        "are vulnerable to XSS attacks and never expire client-side.\n"
                        "Locations:\n" + "\n".join(sample_locations)
                    ),
                    recommendation=(
                        "Implement token expiration checking on the client side, "
                        "or use httpOnly cookies for token storage. Consider adding "
                        "a TTL check that clears tokens after a defined period."
                    ),
                )
            )
            return False

        return True

    def _check_hardcoded_secrets(
        self, src_dir: Path, findings: list[AuditFinding]
    ) -> bool:
        """Grep frontend source for hardcoded URLs, secrets, and credentials.

        Searches for non-localhost URLs, API keys, secrets, and credentials
        hardcoded directly in source files.

        Args:
            src_dir: Path to the frontend src directory.
            findings: List to append any findings to.

        Returns:
            True if no hardcoded secrets found, False otherwise.
        """
        if not src_dir.exists():
            return True

        found_issues: list[tuple[Path, int, str]] = []

        # Pattern 1: Hardcoded non-localhost URLs (http/https not localhost/127.0.0.1)
        url_matches = StaticAnalyzer.grep_pattern(
            src_dir,
            r'["\']https?://(?!localhost|127\.0\.0\.1)[a-zA-Z0-9]',
            [".ts", ".tsx"],
        )
        # Filter out common false positives (comments, test files, type definitions)
        for match in url_matches:
            file_path, line_num, line_content = match
            # Skip comments and common non-secret URLs
            if (
                line_content.strip().startswith("//")
                or line_content.strip().startswith("*")
                or "placeholder" in line_content.lower()
                or "example.com" in line_content.lower()
            ):
                continue
            found_issues.append(match)

        # Pattern 2: API keys, secrets, credentials
        secret_patterns = [
            r'(?i)(api_key|apikey|api_secret|secret_key|auth_token)\s*[=:]\s*["\'][^"\']+["\']',
            r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']',
            r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*",
        ]

        for pattern in secret_patterns:
            matches = StaticAnalyzer.grep_pattern(src_dir, pattern, [".ts", ".tsx"])
            for match in matches:
                _, _, line_content = match
                # Skip comments
                if line_content.strip().startswith("//") or line_content.strip().startswith("*"):
                    continue
                # Skip type definitions and interfaces
                if re.search(r"(type|interface)\s+\w+", line_content):
                    continue
                found_issues.append(match)

        if found_issues:
            sample_locations = [
                f"  - {path.relative_to(src_dir.parent.parent)}:{line}: {content[:80]}"
                for path, line, content in found_issues[:5]
            ]
            if len(found_issues) > 5:
                sample_locations.append(f"  ... and {len(found_issues) - 5} more")

            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-005",
                    title=f"Hardcoded URLs/secrets in frontend source ({len(found_issues)} instances)",
                    severity=Severity.HIGH,
                    description=(
                        "Found hardcoded URLs, API keys, or credentials in frontend "
                        "source files. These should be externalized to environment "
                        "variables.\n"
                        "Locations:\n" + "\n".join(sample_locations)
                    ),
                    recommendation=(
                        "Move all API URLs and secrets to environment variables "
                        "(VITE_* prefix for Vite projects). Never commit secrets "
                        "to source control."
                    ),
                )
            )
            return False

        return True

    def _check_error_interceptors(
        self, src_dir: Path, findings: list[AuditFinding]
    ) -> bool:
        """Verify API client has response error interceptors.

        Checks that the axios (or similar) API client has interceptors
        for handling HTTP error responses with user-facing feedback.

        Args:
            src_dir: Path to the frontend src directory.
            findings: List to append any findings to.

        Returns:
            True if error interceptors are properly configured, False otherwise.
        """
        # Look for API client file
        api_file_candidates = [
            src_dir / "lib" / "api.ts",
            src_dir / "lib" / "api.tsx",
            src_dir / "api" / "client.ts",
            src_dir / "services" / "api.ts",
            src_dir / "utils" / "api.ts",
        ]

        api_file = None
        for candidate in api_file_candidates:
            if candidate.exists():
                api_file = candidate
                break

        if api_file is None:
            # Try to find any file with axios create
            matches = StaticAnalyzer.grep_pattern(
                src_dir, r"axios\.create", [".ts", ".tsx"]
            )
            if matches:
                api_file = matches[0][0]

        if api_file is None:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-006",
                    title="API client file not found",
                    severity=Severity.MEDIUM,
                    description=(
                        "Could not locate an API client configuration file. "
                        "Unable to verify error interceptor setup."
                    ),
                    recommendation=(
                        "Create a centralized API client with proper error "
                        "interceptors for consistent error handling."
                    ),
                )
            )
            return False

        try:
            content = api_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-006",
                    title="Cannot read API client file",
                    severity=Severity.MEDIUM,
                    description=f"Failed to read API client at {api_file}.",
                    file_path=str(api_file),
                    recommendation="Ensure the API client file is readable.",
                )
            )
            return False

        # Check for response interceptor
        has_response_interceptor = bool(
            re.search(r"interceptors\.response\.use", content)
        )

        if not has_response_interceptor:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-006",
                    title="Missing API response error interceptor",
                    severity=Severity.MEDIUM,
                    description=(
                        "The API client does not have a response error interceptor. "
                        "HTTP errors may not be handled consistently across the app."
                    ),
                    file_path=str(api_file),
                    recommendation=(
                        "Add an axios response interceptor to handle common error "
                        "statuses (401, 403, 500) with user-facing feedback."
                    ),
                )
            )
            return False

        # Verify the interceptor handles error cases
        has_error_handling = bool(
            re.search(r"error\.response|status\s*===?\s*4\d{2}|status\s*===?\s*5\d{2}", content)
        )

        if not has_error_handling:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="FE-006",
                    title="Incomplete API error interceptor",
                    severity=Severity.MEDIUM,
                    description=(
                        "The API client has a response interceptor but does not "
                        "appear to handle specific error status codes."
                    ),
                    file_path=str(api_file),
                    recommendation=(
                        "Ensure the response interceptor handles at least 401 "
                        "(unauthorized), 403 (forbidden), and 500 (server error) "
                        "status codes with appropriate user feedback."
                    ),
                )
            )
            return False

        return True
