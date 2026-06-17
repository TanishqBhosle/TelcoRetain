"""Tests for the audit report generator.

Covers weighted score computation, readiness classification at all
boundaries, and report markdown output containing required sections.
"""

import pytest

from audit.models import AuditFinding, PhaseResult, Severity
from audit.report_generator import ReportGenerator


# --- Fixtures ---


def _make_phase(name: str, total: int, passed: int, findings=None) -> PhaseResult:
    """Helper to create a PhaseResult with optional findings."""
    return PhaseResult(
        phase_name=name,
        total_checks=total,
        passed_checks=passed,
        findings=findings or [],
    )


def _make_finding(
    phase: str = "Test Phase",
    severity: Severity = Severity.MEDIUM,
    title: str = "Test Finding",
    description: str = "A test finding",
    recommendation: str = "Fix it",
    file_path: str | None = None,
    line_number: int | None = None,
) -> AuditFinding:
    """Helper to create an AuditFinding."""
    return AuditFinding(
        phase=phase,
        check_id="TEST-001",
        title=title,
        severity=severity,
        description=description,
        file_path=file_path,
        line_number=line_number,
        recommendation=recommendation,
    )


# --- Weighted Score Computation Tests ---


class TestComputeWeightedScore:
    """Tests for ReportGenerator.compute_weighted_score."""

    def test_empty_phases_returns_zero(self):
        assert ReportGenerator.compute_weighted_score([]) == 0.0

    def test_single_unweighted_phase(self):
        phases = [_make_phase("Generic Phase", 10, 8)]
        # score = 8.0, weight = 1.0 => weighted = 8.0
        assert ReportGenerator.compute_weighted_score(phases) == 8.0

    def test_single_weighted_phase_security(self):
        phases = [_make_phase("Security Testing", 10, 7)]
        # score = 7.0, weight = 1.5 => weighted = 7.0
        assert ReportGenerator.compute_weighted_score(phases) == 7.0

    def test_single_weighted_phase_auth(self):
        phases = [_make_phase("Authentication Validation", 10, 9)]
        # score = 9.0, weight = 1.5 => weighted = 9.0
        assert ReportGenerator.compute_weighted_score(phases) == 9.0

    def test_single_weighted_phase_code_quality(self):
        phases = [_make_phase("Code Quality Review", 10, 6)]
        # score = 6.0, weight = 0.75 => weighted = 6.0
        assert ReportGenerator.compute_weighted_score(phases) == 6.0

    def test_multiple_phases_weighted_average(self):
        phases = [
            _make_phase("Authentication Validation", 10, 10),  # score=10, w=1.5
            _make_phase("Security Testing", 10, 10),  # score=10, w=1.5
            _make_phase("Code Quality Review", 10, 10),  # score=10, w=0.75
            _make_phase("Generic Phase", 10, 10),  # score=10, w=1.0
        ]
        # All 10.0 => weighted = 10.0
        assert ReportGenerator.compute_weighted_score(phases) == 10.0

    def test_varied_scores_weighted_correctly(self):
        phases = [
            _make_phase("Authentication Validation", 10, 8),  # score=8.0, w=1.5
            _make_phase("Security Testing", 10, 6),  # score=6.0, w=1.5
            _make_phase("Code Quality Review", 10, 4),  # score=4.0, w=0.75
            _make_phase("Generic Phase", 10, 5),  # score=5.0, w=1.0
        ]
        # weighted_sum = 8.0*1.5 + 6.0*1.5 + 4.0*0.75 + 5.0*1.0
        #             = 12.0 + 9.0 + 3.0 + 5.0 = 29.0
        # total_weight = 1.5 + 1.5 + 0.75 + 1.0 = 4.75
        # weighted = 29.0 / 4.75 = 6.105263... => 6.11
        assert ReportGenerator.compute_weighted_score(phases) == 6.11

    def test_zero_total_checks_phase(self):
        phases = [_make_phase("Empty Phase", 0, 0)]
        # score = 0.0, weight = 1.0 => weighted = 0.0
        assert ReportGenerator.compute_weighted_score(phases) == 0.0

    def test_all_phases_zero_score(self):
        phases = [
            _make_phase("Authentication Validation", 10, 0),
            _make_phase("Security Testing", 10, 0),
            _make_phase("Code Quality Review", 10, 0),
            _make_phase("Generic Phase", 10, 0),
        ]
        assert ReportGenerator.compute_weighted_score(phases) == 0.0


# --- Readiness Classification Tests ---


class TestClassifyReadiness:
    """Tests for ReportGenerator.classify_readiness at all boundaries."""

    def test_score_10_production_ready(self):
        assert ReportGenerator.classify_readiness(10.0) == "Production Ready"

    def test_score_8_production_ready(self):
        assert ReportGenerator.classify_readiness(8.0) == "Production Ready"

    def test_score_7_99_caveats(self):
        assert (
            ReportGenerator.classify_readiness(7.99)
            == "Production Ready with Caveats"
        )

    def test_score_6_caveats(self):
        assert (
            ReportGenerator.classify_readiness(6.0)
            == "Production Ready with Caveats"
        )

    def test_score_5_99_significant_rework(self):
        assert (
            ReportGenerator.classify_readiness(5.99)
            == "Significant Rework Required"
        )

    def test_score_4_significant_rework(self):
        assert (
            ReportGenerator.classify_readiness(4.0)
            == "Significant Rework Required"
        )

    def test_score_3_99_not_production_ready(self):
        assert ReportGenerator.classify_readiness(3.99) == "Not Production Ready"

    def test_score_0_not_production_ready(self):
        assert ReportGenerator.classify_readiness(0.0) == "Not Production Ready"


# --- Report Generation Tests ---


class TestGenerate:
    """Tests for ReportGenerator.generate markdown output."""

    @pytest.fixture
    def sample_phases(self) -> list[PhaseResult]:
        """Create a set of sample phases for report generation tests."""
        critical_finding = _make_finding(
            phase="Security Testing",
            severity=Severity.CRITICAL,
            title="Hardcoded Secret Key",
            description="SECRET_KEY found in source code",
            recommendation="Move to .env file",
            file_path="app/core/config.py",
            line_number=42,
        )
        high_finding = _make_finding(
            phase="Authentication Validation",
            severity=Severity.HIGH,
            title="Weak Token Expiry",
            description="Access tokens expire after 24 hours",
            recommendation="Reduce to 60 minutes maximum",
        )
        medium_finding = _make_finding(
            phase="Code Quality Review",
            severity=Severity.MEDIUM,
            title="Missing Docstrings",
            description="42% of public functions lack docstrings",
            recommendation="Add docstrings to public interfaces",
        )

        return [
            _make_phase(
                "Authentication Validation", 6, 5, findings=[high_finding]
            ),
            _make_phase(
                "Security Testing", 7, 5, findings=[critical_finding]
            ),
            _make_phase(
                "Code Quality Review", 6, 4, findings=[medium_finding]
            ),
            _make_phase("Requirement Validation", 8, 7),
        ]

    def test_report_contains_title(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "# TelcoRetain Platform Audit Report" in report

    def test_report_contains_generated_timestamp(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "**Generated:**" in report

    def test_report_contains_executive_summary(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "## Executive Summary" in report
        assert "**Overall Score:**" in report
        assert "**Readiness:**" in report
        assert "**Critical Findings:** 1" in report
        assert "**High Findings:** 1" in report
        assert "**Medium Findings:** 1" in report

    def test_report_contains_per_phase_sections(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "## Phase: Authentication Validation" in report
        assert "## Phase: Security Testing" in report
        assert "## Phase: Code Quality Review" in report
        assert "## Phase: Requirement Validation" in report

    def test_report_contains_phase_scores(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        # Authentication: 5/6 passed => score = 8.3
        assert "**Score: 8.3/10**" in report
        # Security: 5/7 passed => score = 7.1
        assert "**Score: 7.1/10**" in report

    def test_report_contains_findings_with_severity(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "[Critical] Hardcoded Secret Key" in report
        assert "[High] Weak Token Expiry" in report
        assert "[Medium] Missing Docstrings" in report

    def test_report_contains_file_paths_in_findings(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "`app/core/config.py`" in report

    def test_report_contains_recommendations(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "Move to .env file" in report
        assert "Reduce to 60 minutes maximum" in report

    def test_report_contains_scorecard_table(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "## Final Scorecard" in report
        assert "| Phase | Score | Weight |" in report
        assert "| Authentication Validation | 8.3/10 | 1.5x |" in report
        assert "| Security Testing | 7.1/10 | 1.5x |" in report
        assert "| Code Quality Review | 6.7/10 | 0.75x |" in report
        assert "| Requirement Validation | 8.8/10 | 1.0x |" in report

    def test_report_contains_remediation_list(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "## Prioritized Remediation" in report
        # Critical should come first
        assert "1. **[Critical]** Hardcoded Secret Key" in report
        assert "2. **[High]** Weak Token Expiry" in report

    def test_report_contains_summary_table(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        assert "## Summary" in report
        assert "| Severity | Count |" in report
        assert "| Critical | 1 |" in report
        assert "| High | 1 |" in report
        assert "| Medium | 1 |" in report
        assert "| **Total** | **3** |" in report

    def test_report_with_no_findings(self):
        phases = [
            _make_phase("Phase A", 10, 10),
            _make_phase("Phase B", 5, 5),
        ]
        report = ReportGenerator.generate(phases)
        assert "## Executive Summary" in report
        assert "**Critical Findings:** 0" in report
        assert "**High Findings:** 0" in report
        assert "**Medium Findings:** 0" in report
        assert "No critical or high severity findings." in report

    def test_report_readiness_appears_in_executive_summary(self, sample_phases):
        report = ReportGenerator.generate(sample_phases)
        # Verify the readiness classification is rendered
        overall_score = ReportGenerator.compute_weighted_score(sample_phases)
        readiness = ReportGenerator.classify_readiness(overall_score)
        assert f"**Readiness:** {readiness}" in report
