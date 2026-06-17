"""Report generator for the platform audit.

Computes weighted scores, classifies readiness, and renders
the final consolidated markdown report.
"""

from datetime import datetime

from audit.models import AuditFinding, PhaseResult, Severity


# Phase weight configuration: Security and Authentication get 1.5x,
# Code Quality gets 0.75x, all others get 1.0x.
PHASE_WEIGHTS: dict[str, float] = {
    "Authentication Validation": 1.5,
    "Security Testing": 1.5,
    "Code Quality Review": 0.75,
}

DEFAULT_WEIGHT: float = 1.0


class ReportGenerator:
    """Generates the final audit report from phase results.

    Provides static methods for score computation, readiness
    classification, and full markdown report rendering.
    """

    @staticmethod
    def compute_weighted_score(phase_results: list[PhaseResult]) -> float:
        """Compute the weighted overall score from phase results.

        For each phase, the score is multiplied by its weight.
        The weighted overall score is the sum of weighted scores
        divided by the sum of weights.

        Weights:
          - "Authentication Validation": 1.5
          - "Security Testing": 1.5
          - "Code Quality Review": 0.75
          - All other phases: 1.0

        Args:
            phase_results: List of PhaseResult objects for all phases.

        Returns:
            Weighted overall score as a float. Returns 0.0 if no phases.
        """
        if not phase_results:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for phase in phase_results:
            weight = PHASE_WEIGHTS.get(phase.phase_name, DEFAULT_WEIGHT)
            weighted_sum += phase.score * weight
            total_weight += weight

        if total_weight == 0.0:
            return 0.0

        return weighted_sum / total_weight

    @staticmethod
    def classify_readiness(score: float) -> str:
        """Classify platform readiness based on weighted overall score.

        Thresholds:
          - score >= 8.0: "Production Ready"
          - 6.0 <= score < 8.0: "Production Ready with Caveats"
          - 4.0 <= score < 6.0: "Significant Rework Required"
          - score < 4.0: "Not Production Ready"

        Args:
            score: The weighted overall score (0-10 scale).

        Returns:
            A string classification of production readiness.
        """
        if score >= 8.0:
            return "Production Ready"
        elif score >= 6.0:
            return "Production Ready with Caveats"
        elif score >= 4.0:
            return "Significant Rework Required"
        else:
            return "Not Production Ready"

    @staticmethod
    def generate(phase_results: list[PhaseResult]) -> str:
        """Render complete audit report as markdown.

        Args:
            phase_results: List of PhaseResult objects for all 15 phases.

        Returns:
            Complete markdown report as a string.
        """
        sections: list[str] = []
        sections.append("# TelcoRetain Platform Audit Report\n")
        sections.append(f"**Generated:** {datetime.now().isoformat()}\n")

        # Compute aggregates
        overall_score = ReportGenerator.compute_weighted_score(phase_results)
        readiness = ReportGenerator.classify_readiness(overall_score)

        all_findings: list[AuditFinding] = []
        for pr in phase_results:
            all_findings.extend(pr.findings)

        total_critical = sum(
            1 for f in all_findings if f.severity == Severity.CRITICAL
        )
        total_high = sum(1 for f in all_findings if f.severity == Severity.HIGH)
        total_medium = sum(
            1 for f in all_findings if f.severity == Severity.MEDIUM
        )

        # Executive Summary
        sections.append("## Executive Summary\n")
        sections.append(f"- **Overall Score:** {overall_score:.2f}/10")
        sections.append(f"- **Readiness:** {readiness}")
        sections.append(f"- **Critical Findings:** {total_critical}")
        sections.append(f"- **High Findings:** {total_high}")
        sections.append(f"- **Medium Findings:** {total_medium}\n")

        # Phase sections
        for phase in phase_results:
            sections.append(f"## Phase: {phase.phase_name}")
            sections.append(
                f"**Score: {phase.score}/10** "
                f"({phase.passed_checks}/{phase.total_checks} checks passed)\n"
            )
            for finding in phase.findings:
                sections.append(
                    f"### [{finding.severity.value}] {finding.title}"
                )
                sections.append(f"{finding.description}")
                if finding.file_path:
                    sections.append(f"- **File:** `{finding.file_path}`")
                if finding.recommendation:
                    sections.append(
                        f"- **Recommendation:** {finding.recommendation}"
                    )
                sections.append("")

        # Final Scorecard
        sections.append("## Final Scorecard\n")
        sections.append("| Phase | Score | Weight |")
        sections.append("|-------|-------|--------|")
        for phase in phase_results:
            w = PHASE_WEIGHTS.get(phase.phase_name, DEFAULT_WEIGHT)
            sections.append(f"| {phase.phase_name} | {phase.score}/10 | {w}x |")

        # Remediation
        sections.append("\n## Prioritized Remediation\n")
        critical_findings = [
            f for f in all_findings if f.severity == Severity.CRITICAL
        ]
        high_findings = [
            f for f in all_findings if f.severity == Severity.HIGH
        ]
        for i, f in enumerate(critical_findings + high_findings, 1):
            sections.append(
                f"{i}. **[{f.severity.value}]** {f.title} — {f.recommendation}"
            )

        # Summary table
        sections.append("\n## Findings Summary\n")
        sections.append("| Severity | Count |")
        sections.append("|----------|-------|")
        sections.append(f"| Critical | {total_critical} |")
        sections.append(f"| High | {total_high} |")
        sections.append(f"| Medium | {total_medium} |")

        return "\n".join(sections)
