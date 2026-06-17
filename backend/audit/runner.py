"""Audit runner orchestrator.

Manages the sequential execution of audit phases and collects
their results for downstream report generation.
"""

from pathlib import Path

from audit.models import PhaseResult
from audit.phase import AuditPhase


class AuditRunner:
    """Orchestrates the execution of registered audit phases.

    The runner executes phases sequentially in registration order,
    collecting PhaseResult objects from each. Results are available
    after calling `run()`.

    Attributes:
        workspace_root: Path to the project root being audited.
        phases: Ordered list of audit phase instances to execute.
        results: List of PhaseResults populated after run() completes.
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize the audit runner.

        Args:
            workspace_root: Path to the root of the project being audited.
        """
        self.workspace_root = workspace_root
        self.phases: list[AuditPhase] = []
        self.results: list[PhaseResult] = []

    def register_phase(self, phase: AuditPhase) -> None:
        """Register an audit phase for execution.

        Args:
            phase: An AuditPhase instance to add to the execution pipeline.
        """
        self.phases.append(phase)

    async def run(self) -> list[PhaseResult]:
        """Execute all registered phases sequentially.

        Each phase receives the workspace_root and returns a PhaseResult.
        Results are stored in `self.results` and also returned.

        Returns:
            List of PhaseResult objects, one per registered phase.
        """
        self.results = []
        for phase in self.phases:
            result = await phase.execute(self.workspace_root)
            self.results.append(result)
        return self.results
