"""Core data models for the audit framework.

Defines severity levels, individual audit findings, and phase-level
result containers with scoring logic.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(Enum):
    """Classification of audit finding severity.

    Only Medium and above are reported per audit scope.
    """

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"


@dataclass
class AuditFinding:
    """A single audit finding produced by a phase check.

    Attributes:
        phase: Name of the audit phase that produced this finding.
        check_id: Unique identifier for the specific check (e.g. "REQ-001").
        title: Short summary of the finding.
        severity: Severity classification (Critical, High, or Medium).
        description: Detailed explanation of the finding.
        file_path: Optional path to the relevant source file.
        line_number: Optional line number within the file.
        recommendation: Suggested remediation action.
    """

    phase: str
    check_id: str
    title: str
    severity: Severity
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: str = ""


@dataclass
class PhaseResult:
    """Aggregated result for a single audit phase.

    Attributes:
        phase_name: Display name of the audit phase.
        total_checks: Total number of checks executed in this phase.
        passed_checks: Number of checks that passed without findings.
        findings: List of findings produced by failed checks.
    """

    phase_name: str
    total_checks: int
    passed_checks: int
    findings: list[AuditFinding] = field(default_factory=list)

    @property
    def score(self) -> float:
        """Compute phase score on a 0-10 scale based on pass ratio.

        Returns 0.0 if no checks were executed.
        """
        if self.total_checks == 0:
            return 0.0
        return round((self.passed_checks / self.total_checks) * 10, 1)
