"""Tests for the SecurityScanner utility module."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from audit.utils.security_scanner import SecurityScanner


class TestSecretPatterns:
    """Tests for SECRET_PATTERNS definitions."""

    def test_has_password_pattern(self):
        """SECRET_PATTERNS should detect password assignments."""
        assert len(SecurityScanner.SECRET_PATTERNS) >= 3

    def test_password_pattern_matches(self):
        """Should match password/secret/api_key/token assignments."""
        import re

        pattern = re.compile(SecurityScanner.SECRET_PATTERNS[0])
        assert pattern.search('password = "my_secret_value"')
        assert pattern.search("SECRET = 'abc123'")
        assert pattern.search('api_key = "key-value-here"')
        assert pattern.search('token = "tok_abc123"')

    def test_bearer_token_pattern_matches(self):
        """Should match Bearer token patterns."""
        import re

        pattern = re.compile(SecurityScanner.SECRET_PATTERNS[1])
        assert pattern.search("Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig")
        assert pattern.search("Bearer abc123+/def=")

    def test_postgresql_url_pattern_matches(self):
        """Should match postgresql connection URLs with credentials."""
        import re

        pattern = re.compile(SecurityScanner.SECRET_PATTERNS[2])
        assert pattern.search("postgresql://admin:password123@localhost")
        assert pattern.search("postgresql://user:pass@db.host.com")

    def test_password_pattern_case_insensitive(self):
        """Password pattern should be case-insensitive."""
        import re

        pattern = re.compile(SecurityScanner.SECRET_PATTERNS[0])
        assert pattern.search('PASSWORD = "value"')
        assert pattern.search('Password = "value"')
        assert pattern.search('pAssWoRd = "value"')


class TestSecurityHeaders:
    """Tests for SECURITY_HEADERS list."""

    def test_contains_expected_headers(self):
        assert "X-Content-Type-Options" in SecurityScanner.SECURITY_HEADERS
        assert "X-Frame-Options" in SecurityScanner.SECURITY_HEADERS
        assert "Strict-Transport-Security" in SecurityScanner.SECURITY_HEADERS
        assert "X-XSS-Protection" in SecurityScanner.SECURITY_HEADERS

    def test_has_four_headers(self):
        assert len(SecurityScanner.SECURITY_HEADERS) == 4


class TestScanForSecrets:
    """Tests for scan_for_secrets method."""

    def test_finds_secret_in_python_file(self, tmp_path):
        """Should detect hardcoded password in a .py file."""
        py_file = tmp_path / "config.py"
        py_file.write_text('DB_PASSWORD = "super_secret_123"\n', encoding="utf-8")

        results = SecurityScanner.scan_for_secrets(tmp_path)

        assert len(results) == 1
        assert results[0][0] == py_file
        assert results[0][1] == 1
        assert 'DB_PASSWORD = "super_secret_123"' in results[0][2]

    def test_finds_secret_in_typescript_file(self, tmp_path):
        """Should detect hardcoded token in a .ts file."""
        ts_file = tmp_path / "api.ts"
        ts_file.write_text(
            'const token = "Bearer eyJhbGciOiJIUzI1NiJ9.test.sig"\n',
            encoding="utf-8",
        )

        results = SecurityScanner.scan_for_secrets(tmp_path)

        assert len(results) == 1
        assert results[0][0] == ts_file

    def test_finds_postgresql_url(self, tmp_path):
        """Should detect postgresql connection string with credentials."""
        py_file = tmp_path / "db.py"
        py_file.write_text(
            'DATABASE_URL = "postgresql://admin:pass123@db.host.com/mydb"\n',
            encoding="utf-8",
        )

        results = SecurityScanner.scan_for_secrets(tmp_path)

        assert len(results) == 1
        assert results[0][0] == py_file

    def test_no_false_positives_on_clean_file(self, tmp_path):
        """Should not flag files without secrets."""
        py_file = tmp_path / "clean.py"
        py_file.write_text(
            "import os\n\ndef get_value():\n    return os.environ['KEY']\n",
            encoding="utf-8",
        )

        results = SecurityScanner.scan_for_secrets(tmp_path)
        assert results == []

    def test_excludes_files_matching_patterns(self, tmp_path):
        """Should skip files matching exclude patterns."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_auth.py"
        test_file.write_text('token = "test_token_value"\n', encoding="utf-8")

        # Without exclude, it should find it
        results_no_exclude = SecurityScanner.scan_for_secrets(tmp_path)
        assert len(results_no_exclude) == 1

        # With exclude, it should skip
        results_excluded = SecurityScanner.scan_for_secrets(
            tmp_path, exclude_patterns=["tests/"]
        )
        assert results_excluded == []

    def test_excludes_env_files_pattern(self, tmp_path):
        """Should skip .env-like paths when excluded."""
        env_dir = tmp_path / ".env"
        env_dir.mkdir()
        env_file = env_dir / "config.py"
        env_file.write_text('secret = "value"\n', encoding="utf-8")

        results = SecurityScanner.scan_for_secrets(
            tmp_path, exclude_patterns=[".env"]
        )
        assert results == []

    def test_excludes_pycache(self, tmp_path):
        """Should skip __pycache__ directories when excluded."""
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        cache_file = cache_dir / "module.py"
        cache_file.write_text('password = "cached"\n', encoding="utf-8")

        results = SecurityScanner.scan_for_secrets(
            tmp_path, exclude_patterns=["__pycache__/"]
        )
        assert results == []

    def test_searches_recursively(self, tmp_path):
        """Should find secrets in nested directories."""
        nested = tmp_path / "app" / "core"
        nested.mkdir(parents=True)
        py_file = nested / "settings.py"
        py_file.write_text('api_key = "sk-12345abc"\n', encoding="utf-8")

        results = SecurityScanner.scan_for_secrets(tmp_path)

        assert len(results) == 1
        assert results[0][0] == py_file

    def test_reports_correct_line_number(self, tmp_path):
        """Should report the correct line number for the match."""
        py_file = tmp_path / "multi.py"
        py_file.write_text(
            "import os\nimport sys\n\nsecret = \"leak\"\n\ndef main():\n    pass\n",
            encoding="utf-8",
        )

        results = SecurityScanner.scan_for_secrets(tmp_path)

        assert len(results) == 1
        assert results[0][1] == 4  # Line 4

    def test_one_match_per_line(self, tmp_path):
        """Should report at most one match per line even if multiple patterns match."""
        py_file = tmp_path / "double.py"
        # This line could match both password pattern and bearer pattern
        py_file.write_text(
            'password = "Bearer eyJhbGciOiJIUzI1NiJ9.test.sig"\n',
            encoding="utf-8",
        )

        results = SecurityScanner.scan_for_secrets(tmp_path)

        # Should still be only 1 result (break after first match)
        assert len(results) == 1

    def test_handles_unreadable_file(self, tmp_path):
        """Should gracefully handle files that can't be read."""
        py_file = tmp_path / "binary.py"
        py_file.write_bytes(b"\x80\x81\x82\x83" * 100)

        # Should not raise, returns empty
        results = SecurityScanner.scan_for_secrets(tmp_path)
        assert results == []

    def test_ignores_non_source_extensions(self, tmp_path):
        """Should only scan .py and .ts files, not others."""
        txt_file = tmp_path / "secrets.txt"
        txt_file.write_text('password = "leaked"\n', encoding="utf-8")

        js_file = tmp_path / "config.js"
        js_file.write_text('const secret = "leaked"\n', encoding="utf-8")

        results = SecurityScanner.scan_for_secrets(tmp_path)
        assert results == []

    def test_empty_directory(self, tmp_path):
        """Should return empty list for empty directory."""
        results = SecurityScanner.scan_for_secrets(tmp_path)
        assert results == []

    def test_default_exclude_patterns_is_none(self, tmp_path):
        """Should work when exclude_patterns not specified."""
        py_file = tmp_path / "test.py"
        py_file.write_text('token = "abc123"\n', encoding="utf-8")

        results = SecurityScanner.scan_for_secrets(tmp_path)
        assert len(results) == 1


class TestCheckDependencyVulnerabilities:
    """Tests for check_dependency_vulnerabilities method."""

    def test_returns_empty_for_missing_file(self, tmp_path):
        """Should return empty list if requirements file doesn't exist."""
        result = SecurityScanner.check_dependency_vulnerabilities(
            tmp_path / "requirements.txt"
        )
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_when_pip_audit_not_available(self, mock_run, tmp_path):
        """Should return empty list if pip-audit is not installed."""
        mock_run.side_effect = FileNotFoundError("pip-audit not found")
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n", encoding="utf-8")

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_on_timeout(self, mock_run, tmp_path):
        """Should return empty list if pip-audit times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("pip-audit", 120)
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n", encoding="utf-8")

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_parses_vulnerability_output(self, mock_run, tmp_path):
        """Should parse pip-audit JSON output into vulnerability dicts."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n", encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                {
                    "dependencies": [
                        {
                            "name": "flask",
                            "version": "2.0.0",
                            "vulns": [
                                {
                                    "id": "CVE-2023-1234",
                                    "fix_versions": ["2.3.2"],
                                    "description": "Security issue in Flask",
                                }
                            ],
                        }
                    ]
                }
            ),
            returncode=1,
        )

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)

        assert len(result) == 1
        assert result[0]["name"] == "flask"
        assert result[0]["version"] == "2.0.0"
        assert result[0]["vulnerability_id"] == "CVE-2023-1234"
        assert result[0]["fix_versions"] == ["2.3.2"]
        assert result[0]["description"] == "Security issue in Flask"

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_handles_multiple_vulnerabilities(self, mock_run, tmp_path):
        """Should handle multiple vulns across multiple packages."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\ndjango==3.0.0\n", encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                {
                    "dependencies": [
                        {
                            "name": "flask",
                            "version": "2.0.0",
                            "vulns": [
                                {"id": "CVE-2023-0001", "fix_versions": ["2.3.2"], "description": "Issue 1"},
                            ],
                        },
                        {
                            "name": "django",
                            "version": "3.0.0",
                            "vulns": [
                                {"id": "CVE-2023-0002", "fix_versions": ["3.2.1"], "description": "Issue 2"},
                                {"id": "CVE-2023-0003", "fix_versions": ["3.2.2"], "description": "Issue 3"},
                            ],
                        },
                    ]
                }
            ),
            returncode=1,
        )

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)
        assert len(result) == 3

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_on_invalid_json(self, mock_run, tmp_path):
        """Should return empty list if output is not valid JSON."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n", encoding="utf-8")

        mock_run.return_value = MagicMock(stdout="not json", returncode=1)

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_on_no_output(self, mock_run, tmp_path):
        """Should return empty list if pip-audit produces no output."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n", encoding="utf-8")

        mock_run.return_value = MagicMock(stdout="", returncode=0)

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_handles_list_format_output(self, mock_run, tmp_path):
        """Should handle pip-audit output as a list directly."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n", encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                [
                    {
                        "name": "flask",
                        "version": "2.0.0",
                        "vulns": [
                            {"id": "CVE-2023-1234", "fix_versions": ["2.3.2"], "description": "desc"}
                        ],
                    }
                ]
            ),
            returncode=1,
        )

        result = SecurityScanner.check_dependency_vulnerabilities(req_file)
        assert len(result) == 1
        assert result[0]["name"] == "flask"


class TestCheckNpmVulnerabilities:
    """Tests for check_npm_vulnerabilities method."""

    def test_returns_empty_for_missing_file(self, tmp_path):
        """Should return empty list if package.json doesn't exist."""
        result = SecurityScanner.check_npm_vulnerabilities(
            tmp_path / "package.json"
        )
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_when_npm_not_available(self, mock_run, tmp_path):
        """Should return empty list if npm is not installed."""
        mock_run.side_effect = FileNotFoundError("npm not found")
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_on_timeout(self, mock_run, tmp_path):
        """Should return empty list if npm audit times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("npm", 120)
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_parses_npm_v7_format(self, mock_run, tmp_path):
        """Should parse npm v7+ audit JSON output."""
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                {
                    "vulnerabilities": {
                        "lodash": {
                            "severity": "high",
                            "title": "Prototype Pollution",
                            "url": "https://github.com/advisories/GHSA-1234",
                            "range": "<4.17.21",
                        }
                    }
                }
            ),
            returncode=1,
        )

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)

        assert len(result) == 1
        assert result[0]["name"] == "lodash"
        assert result[0]["severity"] == "high"
        assert result[0]["title"] == "Prototype Pollution"
        assert result[0]["url"] == "https://github.com/advisories/GHSA-1234"
        assert result[0]["range"] == "<4.17.21"

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_parses_npm_v6_format(self, mock_run, tmp_path):
        """Should parse npm v6 audit JSON output (advisories format)."""
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                {
                    "advisories": {
                        "1234": {
                            "module_name": "express",
                            "severity": "moderate",
                            "title": "Open Redirect",
                            "url": "https://npmjs.com/advisories/1234",
                            "range": "<4.18.0",
                        }
                    }
                }
            ),
            returncode=1,
        )

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)

        assert len(result) == 1
        assert result[0]["name"] == "express"
        assert result[0]["severity"] == "moderate"
        assert result[0]["title"] == "Open Redirect"

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_on_invalid_json(self, mock_run, tmp_path):
        """Should return empty list if output is not valid JSON."""
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        mock_run.return_value = MagicMock(stdout="npm ERR!", returncode=1)

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_returns_empty_on_no_output(self, mock_run, tmp_path):
        """Should return empty list if npm audit produces no output."""
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        mock_run.return_value = MagicMock(stdout="", returncode=0)

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)
        assert result == []

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_runs_in_correct_directory(self, mock_run, tmp_path):
        """Should run npm audit in the package.json's parent directory."""
        sub_dir = tmp_path / "frontend"
        sub_dir.mkdir()
        pkg_file = sub_dir / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps({"vulnerabilities": {}}),
            returncode=0,
        )

        SecurityScanner.check_npm_vulnerabilities(pkg_file)

        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("cwd") == str(sub_dir) or \
               (len(call_kwargs) > 1 and call_kwargs[1].get("cwd") == str(sub_dir))

    @patch("audit.utils.security_scanner.subprocess.run")
    def test_handles_multiple_vulnerabilities(self, mock_run, tmp_path):
        """Should handle multiple vulnerabilities in npm v7 format."""
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")

        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                {
                    "vulnerabilities": {
                        "lodash": {
                            "severity": "high",
                            "title": "Prototype Pollution",
                            "url": "https://example.com/1",
                            "range": "<4.17.21",
                        },
                        "minimist": {
                            "severity": "critical",
                            "title": "Prototype Pollution",
                            "url": "https://example.com/2",
                            "range": "<1.2.6",
                        },
                    }
                }
            ),
            returncode=1,
        )

        result = SecurityScanner.check_npm_vulnerabilities(pkg_file)
        assert len(result) == 2
