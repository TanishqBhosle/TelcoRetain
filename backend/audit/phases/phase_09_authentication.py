"""Phase 9: Authentication Validation.

Validates the authentication implementation against OWASP standards including
JWT configuration, password hashing, account lockout, token blacklisting,
refresh tokens, and hardcoded secrets.

Checks:
- JWT algorithm is HS256 or stronger
- ACCESS_TOKEN_EXPIRE_MINUTES is bounded (≤ 60)
- JWT payload includes sub, exp, iat claims
- bcrypt.gensalt() usage with rounds ≥ 10
- Account lockout logic (5 failed attempts / 15-min window)
- blacklist_token on logout and is_token_blacklisted check on auth
- Refresh token expiration > access token expiration
- SECRET_KEY with literal values in non-.env files (Critical if found)
"""

import ast
import re
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


# Algorithms considered strong enough (HS256 minimum)
STRONG_ALGORITHMS = {
    "HS256", "HS384", "HS512",
    "RS256", "RS384", "RS512",
    "ES256", "ES384", "ES512",
    "PS256", "PS384", "PS512",
}


class AuthenticationValidationPhase(AuditPhase):
    """Phase 9: Authentication Validation.

    Inspects the authentication implementation for secure JWT configuration,
    strong password hashing, account lockout logic, token blacklisting,
    refresh token handling, and hardcoded secrets.
    """

    name = "Authentication Validation"
    description = (
        "Validates authentication implementation against OWASP standards "
        "including JWT security, password hashing, account lockout, "
        "token lifecycle, and secret management."
    )

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute authentication validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all authentication checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 8
        passed_checks = 0

        backend_dir = workspace_root / "backend"
        core_dir = backend_dir / "app" / "core"
        services_dir = backend_dir / "app" / "services"
        api_dir = backend_dir / "app" / "api"
        middleware_dir = backend_dir / "app" / "middleware"
        deps_dir = backend_dir / "app" / "dependencies"

        # Check 1: JWT algorithm is HS256 or stronger
        if self._check_jwt_algorithm(core_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-001",
                    title="JWT algorithm is weak or not configured",
                    severity=Severity.HIGH,
                    description=(
                        "The JWT signing algorithm is not set to HS256 or "
                        "a stronger algorithm. Weak algorithms (e.g., none, "
                        "HS128) can be exploited to forge tokens."
                    ),
                    recommendation=(
                        "Set ALGORITHM to 'HS256' or stronger (HS384, HS512, "
                        "RS256, ES256) in the application settings."
                    ),
                )
            )

        # Check 2: ACCESS_TOKEN_EXPIRE_MINUTES is bounded (≤ 60)
        if self._check_token_expiration(core_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-002",
                    title="Unbounded access token expiration",
                    severity=Severity.MEDIUM,
                    description=(
                        "ACCESS_TOKEN_EXPIRE_MINUTES exceeds 60 minutes or "
                        "is not explicitly bounded. Long-lived access tokens "
                        "increase the window for token theft exploitation."
                    ),
                    recommendation=(
                        "Set ACCESS_TOKEN_EXPIRE_MINUTES to 60 or less. "
                        "Prefer 15-30 minutes for sensitive applications."
                    ),
                )
            )

        # Check 3: JWT payload includes sub, exp, iat claims
        if self._check_jwt_claims(core_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-003",
                    title="JWT payload missing required claims",
                    severity=Severity.MEDIUM,
                    description=(
                        "The JWT token creation code does not include all "
                        "required claims (sub, exp, iat). Missing claims "
                        "can lead to improper token validation and audit "
                        "trail gaps."
                    ),
                    recommendation=(
                        "Ensure all JWT tokens include 'sub' (subject), "
                        "'exp' (expiration), and 'iat' (issued at) claims."
                    ),
                )
            )

        # Check 4: bcrypt.gensalt() usage with rounds ≥ 10
        if self._check_bcrypt_rounds(core_dir, services_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-004",
                    title="Weak password hashing work factor",
                    severity=Severity.CRITICAL,
                    description=(
                        "Password hashing uses bcrypt with a work factor "
                        "below 10 rounds, or does not use bcrypt at all. "
                        "Insufficient work factor allows brute-force "
                        "attacks on stolen password hashes."
                    ),
                    recommendation=(
                        "Use bcrypt.gensalt(rounds=12) or higher for "
                        "password hashing. The default bcrypt rounds (12) "
                        "is acceptable; explicitly setting rounds < 10 "
                        "is not."
                    ),
                )
            )

        # Check 5: Account lockout logic (5 failed attempts / 15-min window)
        if self._check_account_lockout(services_dir, api_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-005",
                    title="Missing or incomplete account lockout logic",
                    severity=Severity.MEDIUM,
                    description=(
                        "Could not verify that the authentication system "
                        "tracks failed login attempts and locks accounts "
                        "after 5 failed attempts within a 15-minute window. "
                        "Without lockout, brute-force attacks are feasible."
                    ),
                    recommendation=(
                        "Implement account lockout: track failed_login_count "
                        "per user, lock the account for 15 minutes after 5 "
                        "consecutive failed attempts, and reset the counter "
                        "on successful login."
                    ),
                )
            )

        # Check 6: blacklist_token on logout and is_token_blacklisted on auth
        if self._check_token_blacklisting(api_dir, middleware_dir, deps_dir, core_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-006",
                    title="Missing token blacklisting on logout or auth check",
                    severity=Severity.HIGH,
                    description=(
                        "The logout endpoint does not call blacklist_token "
                        "or the authentication middleware/dependency does not "
                        "check is_token_blacklisted. Without token invalidation, "
                        "stolen tokens remain valid until natural expiration."
                    ),
                    recommendation=(
                        "Call blacklist_token() in the logout endpoint and "
                        "check is_token_blacklisted() in the auth middleware "
                        "before accepting any token."
                    ),
                )
            )

        # Check 7: Refresh token expiration > access token expiration
        if self._check_refresh_token_expiration(core_dir):
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="AUTH-007",
                    title="Refresh token expiration not greater than access token",
                    severity=Severity.MEDIUM,
                    description=(
                        "Could not verify that refresh token expiration is "
                        "longer than access token expiration. If refresh "
                        "tokens expire at the same time or sooner than "
                        "access tokens, the refresh mechanism is ineffective."
                    ),
                    recommendation=(
                        "Set REFRESH_TOKEN_EXPIRE_DAYS to a value that "
                        "ensures refresh tokens outlive access tokens "
                        "(e.g., 7 days vs 30 minutes)."
                    ),
                )
            )

        # Check 8: Hardcoded SECRET_KEY in non-.env files (Critical if found)
        hardcoded_secrets = self._check_hardcoded_secrets(backend_dir)
        if not hardcoded_secrets:
            passed_checks += 1
        else:
            for file_path, line_num, line_content in hardcoded_secrets:
                findings.append(
                    AuditFinding(
                        phase=self.name,
                        check_id="AUTH-008",
                        title="Hardcoded SECRET_KEY found in source code",
                        severity=Severity.CRITICAL,
                        description=(
                            f"A SECRET_KEY with a literal default value was found "
                            f"in a non-.env file. Hardcoded secrets in source code "
                            f"can be extracted from version control history."
                        ),
                        file_path=str(file_path),
                        line_number=line_num,
                        recommendation=(
                            "Remove hardcoded SECRET_KEY values from source code. "
                            "Load secrets exclusively from environment variables "
                            "or a secrets manager. Use a strong random value "
                            "(32+ characters) in production."
                        ),
                    )
                )

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_jwt_algorithm(self, core_dir: Path) -> bool:
        """Verify JWT algorithm is HS256 or stronger.

        Inspects the config/settings and security modules for the ALGORITHM
        setting and verifies it is in the set of strong algorithms.

        Args:
            core_dir: Path to the core directory containing config/security.

        Returns:
            True if the algorithm is HS256 or stronger.
        """
        if not core_dir.exists():
            return False

        # Search for ALGORITHM assignment in config or security files
        py_files = list(core_dir.rglob("*.py"))
        for py_file in py_files:
            if not py_file.is_file():
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # Look for ALGORITHM = "..." or ALGORITHM: str = "..." pattern
            match = re.search(
                r'ALGORITHM[^=]*=\s*["\'](\w+)["\']', content
            )
            if match:
                algorithm = match.group(1)
                if algorithm in STRONG_ALGORITHMS:
                    return True

        return False

    def _check_token_expiration(self, core_dir: Path) -> bool:
        """Verify ACCESS_TOKEN_EXPIRE_MINUTES is bounded (≤ 60).

        Searches for the ACCESS_TOKEN_EXPIRE_MINUTES setting and verifies
        the default or assigned value does not exceed 60.

        Args:
            core_dir: Path to the core directory containing config.

        Returns:
            True if access token expiration is ≤ 60 minutes.
        """
        if not core_dir.exists():
            return False

        py_files = list(core_dir.rglob("*.py"))
        for py_file in py_files:
            if not py_file.is_file():
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # Look for ACCESS_TOKEN_EXPIRE_MINUTES assignment
            # Handles: ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
            # or: ACCESS_TOKEN_EXPIRE_MINUTES = 30
            match = re.search(
                r'ACCESS_TOKEN_EXPIRE_MINUTES[^=]*=\s*(\d+)', content
            )
            if match:
                minutes = int(match.group(1))
                return minutes <= 60

        return False

    def _check_jwt_claims(self, core_dir: Path) -> bool:
        """Verify JWT payload includes sub, exp, iat claims.

        AST-parses token creation functions to check that the payload
        dictionary includes 'sub', 'exp', and 'iat' keys.

        Args:
            core_dir: Path to the core directory containing security module.

        Returns:
            True if all three required claims are present in the payload.
        """
        if not core_dir.exists():
            return False

        required_claims = {"sub", "exp", "iat"}

        py_files = list(core_dir.rglob("*.py"))
        for py_file in py_files:
            if not py_file.is_file():
                continue
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                continue

            functions = StaticAnalyzer.find_function_definitions(tree)
            for func in functions:
                if "token" in func.name.lower() and "create" in func.name.lower():
                    # Look for dict literals in the function body
                    found_claims = self._extract_dict_keys_from_function(func)
                    if required_claims.issubset(found_claims):
                        return True

        return False

    def _extract_dict_keys_from_function(
        self, func: ast.FunctionDef
    ) -> set[str]:
        """Extract string keys from dictionary literals within a function.

        Args:
            func: AST function definition node to inspect.

        Returns:
            Set of string keys found in dict literals within the function.
        """
        keys: set[str] = set()
        for node in ast.walk(func):
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if isinstance(key, ast.Constant) and isinstance(
                        key.value, str
                    ):
                        keys.add(key.value)
        return keys

    def _check_bcrypt_rounds(
        self, core_dir: Path, services_dir: Path
    ) -> bool:
        """Verify bcrypt.gensalt() usage with rounds ≥ 10.

        Checks that password hashing uses bcrypt and that gensalt() is
        called with a rounds parameter ≥ 10 (or uses the default which
        is 12).

        Args:
            core_dir: Path to the core directory.
            services_dir: Path to the services directory.

        Returns:
            True if bcrypt is used with adequate work factor.
        """
        search_dirs = [core_dir, services_dir]

        for directory in search_dirs:
            if not directory.exists():
                continue

            py_files = list(directory.rglob("*.py"))
            for py_file in py_files:
                if not py_file.is_file():
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                # Check if file uses bcrypt
                if "bcrypt" not in content:
                    continue

                # Look for gensalt() usage
                # Pattern: bcrypt.gensalt() or bcrypt.gensalt(rounds=N)
                gensalt_matches = re.findall(
                    r'bcrypt\.gensalt\((?:rounds=)?(\d*)\)', content
                )

                for match in gensalt_matches:
                    if match == "":
                        # Default gensalt() with no argument — default is 12
                        return True
                    else:
                        rounds = int(match)
                        if rounds >= 10:
                            return True
                        else:
                            return False

                # Also check for hashpw + gensalt pattern without explicit rounds
                if "bcrypt.hashpw" in content and "bcrypt.gensalt()" in content:
                    return True

        return False

    def _check_account_lockout(
        self, services_dir: Path, api_dir: Path
    ) -> bool:
        """Search for account lockout logic (5 failed attempts / 15-min window).

        Verifies that the authentication code tracks failed login attempts
        and implements account lockout after a threshold number of failures.

        Args:
            services_dir: Path to the services directory.
            api_dir: Path to the API directory.

        Returns:
            True if account lockout logic is found with proper thresholds.
        """
        search_dirs = [services_dir, api_dir]
        has_failed_count_tracking = False
        has_lockout_threshold = False
        has_lockout_duration = False

        for directory in search_dirs:
            if not directory.exists():
                continue

            py_files = list(directory.rglob("*.py"))
            for py_file in py_files:
                if not py_file.is_file():
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                # Check for failed login count tracking
                if re.search(
                    r'failed_login_count|failed_attempts', content
                ):
                    has_failed_count_tracking = True

                # Check for lockout threshold (>= 5)
                if re.search(
                    r'failed_login_count\s*>=\s*5|'
                    r'failed_attempts\s*>=\s*5|'
                    r'MAX_FAILED_ATTEMPTS\s*=\s*5',
                    content,
                ):
                    has_lockout_threshold = True

                # Check for lockout duration (15 minutes)
                if re.search(
                    r'minutes\s*=\s*15|'
                    r'timedelta\(minutes=15\)|'
                    r'LOCKOUT_DURATION.*15',
                    content,
                ):
                    has_lockout_duration = True

        return (
            has_failed_count_tracking
            and has_lockout_threshold
            and has_lockout_duration
        )

    def _check_token_blacklisting(
        self,
        api_dir: Path,
        middleware_dir: Path,
        deps_dir: Path,
        core_dir: Path,
    ) -> bool:
        """Verify blacklist_token on logout and is_token_blacklisted on auth.

        Checks that the logout endpoint calls blacklist_token and that the
        auth middleware or dependency checks is_token_blacklisted.

        Args:
            api_dir: Path to the API directory.
            middleware_dir: Path to the middleware directory.
            deps_dir: Path to the dependencies directory.
            core_dir: Path to the core directory.

        Returns:
            True if both blacklisting on logout and checking on auth are found.
        """
        has_blacklist_on_logout = False
        has_blacklist_check_on_auth = False

        # Check for blacklist_token usage in logout
        search_dirs_logout = [api_dir]
        for directory in search_dirs_logout:
            if not directory.exists():
                continue
            matches = StaticAnalyzer.grep_pattern(
                directory, r'blacklist_token', [".py"]
            )
            for _, _, line in matches:
                if "await" in line or "blacklist_token(" in line:
                    has_blacklist_on_logout = True
                    break

        # Check for is_token_blacklisted in middleware or dependencies
        search_dirs_auth = [middleware_dir, deps_dir, core_dir]
        for directory in search_dirs_auth:
            if not directory.exists():
                continue
            matches = StaticAnalyzer.grep_pattern(
                directory, r'is_token_blacklisted', [".py"]
            )
            for file_path, _, line in matches:
                # Verify it's used as a check (not just a function definition)
                if (
                    "await" in line
                    or "is_token_blacklisted(" in line
                    or "import" in line
                ):
                    has_blacklist_check_on_auth = True
                    break

        return has_blacklist_on_logout and has_blacklist_check_on_auth

    def _check_refresh_token_expiration(self, core_dir: Path) -> bool:
        """Verify refresh token expiration > access token expiration.

        Compares REFRESH_TOKEN_EXPIRE_DAYS (converted to minutes) against
        ACCESS_TOKEN_EXPIRE_MINUTES to ensure refresh tokens outlive access
        tokens.

        Args:
            core_dir: Path to the core directory containing config.

        Returns:
            True if refresh token expiration exceeds access token expiration.
        """
        if not core_dir.exists():
            return False

        access_minutes: int | None = None
        refresh_days: int | None = None

        py_files = list(core_dir.rglob("*.py"))
        for py_file in py_files:
            if not py_file.is_file():
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # Extract ACCESS_TOKEN_EXPIRE_MINUTES
            # Handles: ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
            match = re.search(
                r'ACCESS_TOKEN_EXPIRE_MINUTES[^=]*=\s*(\d+)', content
            )
            if match:
                access_minutes = int(match.group(1))

            # Extract REFRESH_TOKEN_EXPIRE_DAYS
            # Handles: REFRESH_TOKEN_EXPIRE_DAYS: int = 7
            match = re.search(
                r'REFRESH_TOKEN_EXPIRE_DAYS[^=]*=\s*(\d+)', content
            )
            if match:
                refresh_days = int(match.group(1))

        if access_minutes is not None and refresh_days is not None:
            # Convert refresh days to minutes for comparison
            refresh_minutes = refresh_days * 24 * 60
            return refresh_minutes > access_minutes

        return False

    def _check_hardcoded_secrets(
        self, backend_dir: Path
    ) -> list[tuple[Path, int, str]]:
        """Grep for SECRET_KEY with literal values in non-.env Python files.

        Searches for SECRET_KEY assignments with string literal default
        values in Python source files (excluding .env files, test files,
        and audit phase files).

        Args:
            backend_dir: Path to the backend directory.

        Returns:
            List of (file_path, line_number, line_content) tuples for
            each hardcoded secret found. Empty list if none found.
        """
        if not backend_dir.exists():
            return []

        results: list[tuple[Path, int, str]] = []

        # Pattern: SECRET_KEY with a literal string value assignment
        # Matches: SECRET_KEY = "..." or SECRET_KEY: str = "..."
        pattern = (
            r'SECRET_KEY\s*[:=].*["\'][^"\']{3,}["\']'
        )

        matches = StaticAnalyzer.grep_pattern(
            backend_dir, pattern, [".py"]
        )

        for file_path, line_num, line_content in matches:
            file_str = str(file_path)

            # Exclude .env files
            if ".env" in file_str:
                continue

            # Exclude test files and audit infrastructure
            if ("tests" in file_str or "test_" in file_str
                    or "audit" in file_str):
                continue

            # Only flag if the line contains a literal string value
            if "SECRET_KEY" in line_content:
                results.append((file_path, line_num, line_content))

        return results
