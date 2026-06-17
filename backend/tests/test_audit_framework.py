"""Tests for the audit framework core infrastructure."""

import pytest
import pytest_asyncio
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.runner import AuditRunner


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        assert Severity.CRITICAL.value == "Critical"
        assert Severity.HIGH.value == "High"
        assert Severity.MEDIUM.value == "Medium"

    def test_severity_has_three_levels(self):
        assert len(Severity) == 3


class TestAuditFinding:
    """Tests for AuditFinding dataclass."""

    def test_create_finding_with_required_fields(self):
        finding = AuditFinding(
            phase="Test Phase",
            check_id="TST-001",
            title="Test finding",
            severity=Severity.HIGH,
            description="A test finding description",
        )
        assert finding.phase == "Test Phase"
        assert finding.check_id == "TST-001"
        assert finding.title == "Test finding"
        assert finding.severity == Severity.HIGH
        assert finding.description == "A test finding description"
        assert finding.file_path is None
        assert finding.line_number is None
        assert finding.recommendation == ""

    def test_create_finding_with_all_fields(self):
        finding = AuditFinding(
            phase="Security",
            check_id="SEC-003",
            title="Hardcoded secret",
            severity=Severity.CRITICAL,
            description="Found hardcoded API key",
            file_path="backend/app/core/config.py",
            line_number=42,
            recommendation="Move secret to .env file",
        )
        assert finding.file_path == "backend/app/core/config.py"
        assert finding.line_number == 42
        assert finding.recommendation == "Move secret to .env file"


class TestPhaseResult:
    """Tests for PhaseResult dataclass and scoring."""

    def test_perfect_score(self):
        result = PhaseResult(phase_name="Test", total_checks=10, passed_checks=10)
        assert result.score == 10.0

    def test_zero_score(self):
        result = PhaseResult(phase_name="Test", total_checks=10, passed_checks=0)
        assert result.score == 0.0

    def test_partial_score(self):
        result = PhaseResult(phase_name="Test", total_checks=10, passed_checks=7)
        assert result.score == 7.0

    def test_score_with_no_checks(self):
        result = PhaseResult(phase_name="Test", total_checks=0, passed_checks=0)
        assert result.score == 0.0

    def test_score_rounding(self):
        result = PhaseResult(phase_name="Test", total_checks=3, passed_checks=1)
        assert result.score == 3.3

    def test_findings_default_empty(self):
        result = PhaseResult(phase_name="Test", total_checks=5, passed_checks=5)
        assert result.findings == []

    def test_findings_populated(self):
        finding = AuditFinding(
            phase="Test",
            check_id="TST-001",
            title="Issue",
            severity=Severity.MEDIUM,
            description="desc",
        )
        result = PhaseResult(
            phase_name="Test",
            total_checks=5,
            passed_checks=4,
            findings=[finding],
        )
        assert len(result.findings) == 1
        assert result.findings[0].check_id == "TST-001"


class TestAuditPhase:
    """Tests for AuditPhase abstract base class."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            AuditPhase()

    def test_concrete_phase_must_implement_execute(self):
        class IncompletePhase(AuditPhase):
            name = "Incomplete"
            description = "Missing execute"

        with pytest.raises(TypeError):
            IncompletePhase()

    def test_concrete_phase_can_be_instantiated(self):
        class ConcretePhase(AuditPhase):
            name = "Concrete"
            description = "A concrete phase"

            async def execute(self, workspace_root: Path) -> PhaseResult:
                return PhaseResult(
                    phase_name=self.name,
                    total_checks=1,
                    passed_checks=1,
                )

        phase = ConcretePhase()
        assert phase.name == "Concrete"
        assert phase.description == "A concrete phase"


class TestAuditRunner:
    """Tests for AuditRunner orchestrator."""

    def _make_phase(self, name: str, total: int, passed: int, findings=None):
        """Helper to create a concrete phase for testing."""
        _findings = findings or []

        class _TestPhase(AuditPhase):
            nonlocal name, total, passed, _findings

            async def execute(self, workspace_root: Path) -> PhaseResult:
                return PhaseResult(
                    phase_name=self.name,
                    total_checks=total,
                    passed_checks=passed,
                    findings=_findings,
                )

        _TestPhase.name = name
        _TestPhase.description = f"Test phase: {name}"
        return _TestPhase()

    def test_runner_init(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        assert runner.workspace_root == tmp_path
        assert runner.phases == []
        assert runner.results == []

    def test_register_phase(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        phase = self._make_phase("Phase 1", 5, 5)
        runner.register_phase(phase)
        assert len(runner.phases) == 1
        assert runner.phases[0].name == "Phase 1"

    @pytest.mark.asyncio
    async def test_run_single_phase(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        runner.register_phase(self._make_phase("Phase 1", 10, 8))

        results = await runner.run()

        assert len(results) == 1
        assert results[0].phase_name == "Phase 1"
        assert results[0].total_checks == 10
        assert results[0].passed_checks == 8
        assert results[0].score == 8.0

    @pytest.mark.asyncio
    async def test_run_multiple_phases(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        runner.register_phase(self._make_phase("Phase 1", 10, 10))
        runner.register_phase(self._make_phase("Phase 2", 5, 3))
        runner.register_phase(self._make_phase("Phase 3", 8, 0))

        results = await runner.run()

        assert len(results) == 3
        assert results[0].score == 10.0
        assert results[1].score == 6.0
        assert results[2].score == 0.0

    @pytest.mark.asyncio
    async def test_run_preserves_order(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        for i in range(5):
            runner.register_phase(self._make_phase(f"Phase {i}", 1, 1))

        results = await runner.run()

        for i, result in enumerate(results):
            assert result.phase_name == f"Phase {i}"

    @pytest.mark.asyncio
    async def test_run_stores_results(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        runner.register_phase(self._make_phase("Phase 1", 5, 5))

        await runner.run()

        assert len(runner.results) == 1
        assert runner.results[0].phase_name == "Phase 1"

    @pytest.mark.asyncio
    async def test_run_with_no_phases(self, tmp_path):
        runner = AuditRunner(workspace_root=tmp_path)
        results = await runner.run()
        assert results == []

    @pytest.mark.asyncio
    async def test_run_collects_findings(self, tmp_path):
        finding = AuditFinding(
            phase="Security",
            check_id="SEC-001",
            title="Issue found",
            severity=Severity.CRITICAL,
            description="Critical issue",
        )
        runner = AuditRunner(workspace_root=tmp_path)
        runner.register_phase(self._make_phase("Security", 5, 4, [finding]))

        results = await runner.run()

        assert len(results[0].findings) == 1
        assert results[0].findings[0].severity == Severity.CRITICAL
