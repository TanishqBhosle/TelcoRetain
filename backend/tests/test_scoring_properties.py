"""Property-based tests for scoring and classification logic.

**Validates: Requirements 15.2, 15.3**

Tests the weighted scorecard calculation and readiness classification
using hypothesis to verify properties hold across all valid inputs.
"""

import sys
from pathlib import Path

# Ensure audit package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hypothesis import given, settings, assume
from hypothesis.strategies import floats, integers, lists, composite

from audit.models import PhaseResult
from audit.report_generator import (
    ReportGenerator,
    PHASE_WEIGHTS,
    DEFAULT_WEIGHT,
)


# --------------------------------------------------------------------------
# Strategies
# --------------------------------------------------------------------------

# The 15 canonical phase names used in the audit
PHASE_NAMES = [
    "Requirement Validation",
    "Frontend Validation",
    "Backend Validation",
    "Database Validation",
    "Dataset Validation",
    "ML Model Validation",
    "SHAP Validation",
    "Recommendation Engine Validation",
    "Authentication Validation",  # weight 1.5
    "RBAC Validation",
    "End-to-End Flow Testing",
    "Performance Testing",
    "Security Testing",  # weight 1.5
    "Code Quality Review",  # weight 0.75
    "Final Scorecard",
]


@composite
def phase_result_with_score(draw, phase_name: str):
    """Generate a PhaseResult that yields a specific score in [0, 10].

    We generate total_checks (1-100) and passed_checks (0..total_checks)
    to produce a realistic PhaseResult with a valid score property.
    """
    total_checks = draw(integers(min_value=1, max_value=100))
    passed_checks = draw(integers(min_value=0, max_value=total_checks))
    return PhaseResult(
        phase_name=phase_name,
        total_checks=total_checks,
        passed_checks=passed_checks,
    )


@composite
def all_phase_results(draw):
    """Generate a full set of 15 PhaseResult objects."""
    results = []
    for name in PHASE_NAMES:
        pr = draw(phase_result_with_score(name))
        results.append(pr)
    return results


# --------------------------------------------------------------------------
# Property 15: Weighted Scorecard Calculation
# --------------------------------------------------------------------------


class TestWeightedScorecardCalculation:
    """Property 15: Weighted Scorecard Calculation.

    **Validates: Requirements 15.2**

    For any set of 15 phase scores (each between 0 and 10), the weighted
    overall score SHALL equal the sum of (phase_score × weight) divided by
    the sum of weights, where Security and Authentication phases use weight
    1.5 and Code Quality uses weight 0.75.
    """

    @given(phase_results=all_phase_results())
    @settings(max_examples=30)
    def test_weighted_score_matches_manual_formula(
        self, phase_results: list[PhaseResult]
    ):
        """The computed weighted score must match the manual formula.

        **Validates: Requirements 15.2**

        Formula: Σ(score_i × weight_i) / Σ(weight_i)
        where:
          - "Authentication Validation" has weight 1.5
          - "Security Testing" has weight 1.5
          - "Code Quality Review" has weight 0.75
          - All others have weight 1.0
        """
        # Compute expected value manually
        weighted_sum = 0.0
        total_weight = 0.0
        for pr in phase_results:
            weight = PHASE_WEIGHTS.get(pr.phase_name, DEFAULT_WEIGHT)
            weighted_sum += pr.score * weight
            total_weight += weight

        expected = weighted_sum / total_weight

        # Compute using the implementation
        actual = ReportGenerator.compute_weighted_score(phase_results)

        # Allow floating-point tolerance
        assert abs(actual - expected) < 1e-9, (
            f"Expected {expected}, got {actual}"
        )

    @given(phase_results=all_phase_results())
    @settings(max_examples=30)
    def test_weighted_score_bounded_zero_to_ten(
        self, phase_results: list[PhaseResult]
    ):
        """The weighted score must always be between 0 and 10 (inclusive).

        **Validates: Requirements 15.2**

        Since each phase score is in [0, 10] and weights are positive,
        the weighted average must also be in [0, 10].
        """
        score = ReportGenerator.compute_weighted_score(phase_results)
        assert 0.0 <= score <= 10.0, (
            f"Weighted score {score} is out of [0, 10] range"
        )

    @given(phase_results=all_phase_results())
    @settings(max_examples=30)
    def test_weighted_score_uses_correct_weights(
        self, phase_results: list[PhaseResult]
    ):
        """Verify the specific weights are applied correctly.

        **Validates: Requirements 15.2**

        Authentication Validation: 1.5x
        Security Testing: 1.5x
        Code Quality Review: 0.75x
        All others: 1.0x
        Total weight sum: 12 * 1.0 + 1.5 + 1.5 + 0.75 = 15.75
        """
        expected_total_weight = 12 * 1.0 + 1.5 + 1.5 + 0.75  # = 15.75

        # Verify by computing weight sum from the config
        computed_total = sum(
            PHASE_WEIGHTS.get(pr.phase_name, DEFAULT_WEIGHT)
            for pr in phase_results
        )

        assert abs(computed_total - expected_total_weight) < 1e-9, (
            f"Total weight should be {expected_total_weight}, got {computed_total}"
        )


# --------------------------------------------------------------------------
# Property 16: Readiness Classification Correctness
# --------------------------------------------------------------------------


class TestReadinessClassificationCorrectness:
    """Property 16: Readiness Classification Correctness.

    **Validates: Requirements 15.3**

    For any weighted overall score, the readiness classification SHALL be:
    - "Production Ready" if score >= 8.0
    - "Production Ready with Caveats" if 6.0 <= score < 8.0
    - "Significant Rework Required" if 4.0 <= score < 6.0
    - "Not Production Ready" if score < 4.0
    """

    @given(
        score=floats(min_value=8.0, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=30)
    def test_production_ready_threshold(self, score: float):
        """Scores >= 8.0 must classify as 'Production Ready'.

        **Validates: Requirements 15.3**
        """
        result = ReportGenerator.classify_readiness(score)
        assert result == "Production Ready", (
            f"Score {score} should be 'Production Ready', got '{result}'"
        )

    @given(
        score=floats(
            min_value=6.0,
            max_value=8.0,
            allow_nan=False,
            allow_infinity=False,
            exclude_max=True,
        )
    )
    @settings(max_examples=30)
    def test_production_ready_with_caveats_threshold(self, score: float):
        """Scores in [6.0, 8.0) must classify as 'Production Ready with Caveats'.

        **Validates: Requirements 15.3**
        """
        result = ReportGenerator.classify_readiness(score)
        assert result == "Production Ready with Caveats", (
            f"Score {score} should be 'Production Ready with Caveats', got '{result}'"
        )

    @given(
        score=floats(
            min_value=4.0,
            max_value=6.0,
            allow_nan=False,
            allow_infinity=False,
            exclude_max=True,
        )
    )
    @settings(max_examples=30)
    def test_significant_rework_required_threshold(self, score: float):
        """Scores in [4.0, 6.0) must classify as 'Significant Rework Required'.

        **Validates: Requirements 15.3**
        """
        result = ReportGenerator.classify_readiness(score)
        assert result == "Significant Rework Required", (
            f"Score {score} should be 'Significant Rework Required', got '{result}'"
        )

    @given(
        score=floats(
            min_value=0.0,
            max_value=4.0,
            allow_nan=False,
            allow_infinity=False,
            exclude_max=True,
        )
    )
    @settings(max_examples=30)
    def test_not_production_ready_threshold(self, score: float):
        """Scores < 4.0 must classify as 'Not Production Ready'.

        **Validates: Requirements 15.3**
        """
        result = ReportGenerator.classify_readiness(score)
        assert result == "Not Production Ready", (
            f"Score {score} should be 'Not Production Ready', got '{result}'"
        )

    @given(
        score=floats(
            min_value=0.0,
            max_value=10.0,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    @settings(max_examples=30)
    def test_classification_covers_all_scores(self, score: float):
        """Every valid score must map to exactly one classification.

        **Validates: Requirements 15.3**
        """
        valid_classifications = {
            "Production Ready",
            "Production Ready with Caveats",
            "Significant Rework Required",
            "Not Production Ready",
        }
        result = ReportGenerator.classify_readiness(score)
        assert result in valid_classifications, (
            f"Score {score} produced unexpected classification '{result}'"
        )
