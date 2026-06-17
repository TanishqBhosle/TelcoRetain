"""Security scanner utilities for the audit framework.

Provides specialized utilities for security-focused checks including
secret detection in source code, Python dependency vulnerability scanning
via pip-audit, and Node.js dependency vulnerability scanning via npm audit.
"""

import json
import re
import subprocess
from pathlib import Path


class SecurityScanner:
    """Utilities for security scanning across the codebase.

    Provides class methods for:
    - Scanning source files for hardcoded secrets
    - Checking Python dependencies for known vulnerabilities
    - Checking npm dependencies for known vulnerabilities
    """

    SECRET_PATTERNS = [
        r"(?i)(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*",
        r"postgresql://\w+:\w+@",
    ]

    SECURITY_HEADERS = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Strict-Transport-Security",
        "X-XSS-Protection",
    ]

    SOURCE_EXTENSIONS = [".py", ".ts"]

    @classmethod
    def scan_for_secrets(
        cls, directory: Path, exclude_patterns: list[str] | None = None
    ) -> list[tuple[Path, int, str]]:
        """Scan source files for hardcoded secrets.

        Recursively searches .py and .ts files in the given directory,
        checking each line against SECRET_PATTERNS. Files matching any
        of the exclude_patterns are skipped.

        Args:
            directory: Root directory to scan recursively.
            exclude_patterns: List of path substrings to exclude
                (e.g., ['.env', 'tests/', '__pycache__/']).

        Returns:
            List of (file_path, line_number, matching_line) tuples for
            each detected secret pattern match.
        """
        if exclude_patterns is None:
            exclude_patterns = []

        results: list[tuple[Path, int, str]] = []
        compiled_patterns = [re.compile(p) for p in cls.SECRET_PATTERNS]

        for ext in cls.SOURCE_EXTENSIONS:
            for file_path in directory.rglob(f"*{ext}"):
                # Check if file should be excluded (normalize to forward
                # slashes for cross-platform pattern matching)
                file_str = str(file_path).replace("\\", "/")
                if any(excl in file_str for excl in exclude_patterns):
                    continue

                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                except (OSError, UnicodeDecodeError):
                    continue

                for line_num, line in enumerate(lines, start=1):
                    for pattern in compiled_patterns:
                        if pattern.search(line):
                            results.append((file_path, line_num, line.strip()))
                            break  # One match per line is sufficient

        return results

    @classmethod
    def check_dependency_vulnerabilities(cls, requirements_path: Path) -> list[dict]:
        """Run pip-audit on a requirements file to check for vulnerabilities.

        Attempts to invoke pip-audit with JSON output format. If pip-audit
        is not installed or fails, returns an empty list.

        Args:
            requirements_path: Path to the requirements.txt file.

        Returns:
            List of vulnerability dicts with keys: name, version,
            vulnerability_id, fix_versions, and description.
            Returns empty list if pip-audit is unavailable or fails.
        """
        if not requirements_path.exists():
            return []

        try:
            result = subprocess.run(
                [
                    "pip-audit",
                    "--requirement",
                    str(requirements_path),
                    "--format",
                    "json",
                    "--output",
                    "-",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return []

        # pip-audit returns exit code 1 when vulnerabilities found,
        # but still produces valid JSON output
        output = result.stdout.strip()
        if not output:
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []

        vulnerabilities: list[dict] = []
        # pip-audit JSON format: {"dependencies": [...]}
        dependencies = data if isinstance(data, list) else data.get("dependencies", [])

        for dep in dependencies:
            vulns = dep.get("vulns", [])
            for vuln in vulns:
                vulnerabilities.append(
                    {
                        "name": dep.get("name", ""),
                        "version": dep.get("version", ""),
                        "vulnerability_id": vuln.get("id", ""),
                        "fix_versions": vuln.get("fix_versions", []),
                        "description": vuln.get("description", ""),
                    }
                )

        return vulnerabilities

    @classmethod
    def check_npm_vulnerabilities(cls, package_json_path: Path) -> list[dict]:
        """Run npm audit on a package.json directory to check for vulnerabilities.

        Attempts to invoke npm audit with JSON output format in the directory
        containing the package.json. If npm is not installed or audit fails,
        returns an empty list.

        Args:
            package_json_path: Path to the package.json file.

        Returns:
            List of vulnerability dicts with keys: name, severity,
            title, url, and range.
            Returns empty list if npm is unavailable or audit fails.
        """
        if not package_json_path.exists():
            return []

        working_dir = package_json_path.parent

        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(working_dir),
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return []

        output = result.stdout.strip()
        if not output:
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []

        vulnerabilities: list[dict] = []

        # npm audit JSON format varies between npm versions
        # npm v7+: {"vulnerabilities": {"pkg_name": {...}}}
        # npm v6: {"advisories": {"id": {...}}}
        if "vulnerabilities" in data:
            for pkg_name, vuln_info in data["vulnerabilities"].items():
                vulnerabilities.append(
                    {
                        "name": pkg_name,
                        "severity": vuln_info.get("severity", "unknown"),
                        "title": vuln_info.get("title", ""),
                        "url": vuln_info.get("url", ""),
                        "range": vuln_info.get("range", ""),
                    }
                )
        elif "advisories" in data:
            for _advisory_id, advisory in data["advisories"].items():
                vulnerabilities.append(
                    {
                        "name": advisory.get("module_name", ""),
                        "severity": advisory.get("severity", "unknown"),
                        "title": advisory.get("title", ""),
                        "url": advisory.get("url", ""),
                        "range": advisory.get("range", ""),
                    }
                )

        return vulnerabilities
