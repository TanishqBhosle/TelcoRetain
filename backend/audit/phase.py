"""Abstract base class for audit phases.

Each audit phase implements the AuditPhase interface, providing
a name, description, and an async execute method that inspects
the workspace and returns a PhaseResult.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from audit.models import PhaseResult


class AuditPhase(ABC):
    """Base class for all audit phases.

    Subclasses must define `name` and `description` attributes,
    and implement the `execute` method.

    Attributes:
        name: Short identifier for the phase (e.g. "Requirement Validation").
        description: Human-readable description of what this phase audits.
    """

    name: str
    description: str

    @abstractmethod
    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute the audit phase against the given workspace.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult containing the checks performed and any findings.
        """
        ...
