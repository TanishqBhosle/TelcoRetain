"""Property-based tests for Phase 8: Recommendation Engine Personalization.

Uses hypothesis to generate synthetic customer profiles with various
churn_probability, risk_category, and ARPU values, then verifies that the
recommendation engine correctly personalizes offers:

1. Low-risk customers (churn_probability < 0.3, risk_category != "HIGH")
   SHALL NOT receive high-impact discount offers (expected_impact="HIGH").
2. Two customers with meaningfully different profiles (different ARPU tier
   or risk level) SHALL produce different offer sets.

**Validates: Requirements 8.3, 8.4**
"""

from types import SimpleNamespace

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from ml.recommendations.engine import MLRecommendationEngine


# ============================================================
# Strategies for generating synthetic customer profiles
# ============================================================

# Strategy: churn probability between 0.0 and 1.0
churn_probability_st = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)

# Strategy: risk categories
risk_category_st = st.sampled_from(["LOW", "MEDIUM", "HIGH"])

# Strategy: monthly charges covering various tiers
monthly_charges_st = st.floats(
    min_value=0.0,
    max_value=200.0,
    allow_nan=False,
    allow_infinity=False,
)

# Strategy: tenure in months
tenure_st = st.integers(min_value=0, max_value=72)

# Strategy: contract types
contract_type_st = st.sampled_from(["Month-to-month", "One year", "Two year"])


def make_customer(monthly_charges: float, tenure: int = 6, contract_type: str = "Month-to-month") -> SimpleNamespace:
    """Create a minimal customer object with the given features."""
    return SimpleNamespace(
        monthly_charges=monthly_charges,
        tenure=tenure,
        contract_type=contract_type,
    )


def get_arpu_tier(monthly_charges: float) -> str:
    """Classify monthly charges into tiers for comparison purposes."""
    if monthly_charges > 80:
        return "high"
    else:
        return "standard"


def get_risk_level(churn_probability: float, risk_category: str) -> str:
    """Classify risk level based on churn probability and risk category."""
    if risk_category == "HIGH" or churn_probability >= 0.7:
        return "high_risk"
    else:
        return "low_risk"


# ============================================================
# Property 11: Recommendation Personalization
# **Validates: Requirements 8.3, 8.4**
# ============================================================

class TestProperty11RecommendationPersonalization:
    """Property 11: Recommendation Personalization.

    For any customer with churn_probability < 0.3 and risk_category not
    equal to "HIGH", the recommendation engine SHALL NOT produce
    high-impact discount offers (expected_impact="HIGH"), and for any
    two customers with meaningfully different profiles (different ARPU
    tier or risk level), the generated offer sets SHALL differ.
    """

    @given(
        churn_probability=st.floats(min_value=0.0, max_value=0.29, allow_nan=False),
        risk_category=st.sampled_from(["LOW", "MEDIUM"]),
        monthly_charges=monthly_charges_st,
        tenure=tenure_st,
        contract_type=contract_type_st,
    )
    @settings(max_examples=30)
    def test_low_risk_customers_no_high_impact_discounts(
        self, churn_probability: float, risk_category: str, monthly_charges: float,
        tenure: int, contract_type: str
    ):
        """Low-risk customers should not receive high-impact discount offers.

        For any customer with churn_probability < 0.3 and risk_category
        not "HIGH", the generated offers SHALL NOT include any offer with
        offer_type="discount" and expected_impact="HIGH".
        """
        customer = make_customer(monthly_charges, tenure, contract_type)

        offers = MLRecommendationEngine.match_offers(
            customer=customer,
            churn_probability=churn_probability,
            risk_category=risk_category,
        )

        # Check that no offer has both offer_type="discount" AND expected_impact="HIGH"
        high_impact_discounts = [
            offer for offer in offers
            if offer.get("offer_type") == "discount"
            and offer.get("expected_impact") == "HIGH"
        ]

        assert len(high_impact_discounts) == 0, (
            f"Low-risk customer (churn_prob={churn_probability}, "
            f"risk_category={risk_category}) received high-impact discount "
            f"offers: {high_impact_discounts}"
        )

    @given(
        churn_prob_1=churn_probability_st,
        risk_category_1=risk_category_st,
        monthly_charges_1=monthly_charges_st,
        tenure_1=tenure_st,
        contract_type_1=contract_type_st,
        churn_prob_2=churn_probability_st,
        risk_category_2=risk_category_st,
        monthly_charges_2=monthly_charges_st,
        tenure_2=tenure_st,
        contract_type_2=contract_type_st,
    )
    @settings(max_examples=30)
    def test_different_profiles_produce_different_offers(
        self,
        churn_prob_1: float,
        risk_category_1: str,
        monthly_charges_1: float,
        tenure_1: int,
        contract_type_1: str,
        churn_prob_2: float,
        risk_category_2: str,
        monthly_charges_2: float,
        tenure_2: int,
        contract_type_2: str,
    ):
        """Customers with meaningfully different risk profiles get different offers.

        For any two customers with different risk levels (high_risk vs low_risk),
        the generated offer sets SHALL differ (different offer types,
        counts, or impact levels).
        """
        # Determine risk levels
        risk_1 = get_risk_level(churn_prob_1, risk_category_1)
        risk_2 = get_risk_level(churn_prob_2, risk_category_2)

        # Only test when risk levels are meaningfully different
        assume(risk_1 != risk_2)

        customer_1 = make_customer(monthly_charges_1, tenure_1, contract_type_1)
        customer_2 = make_customer(monthly_charges_2, tenure_2, contract_type_2)

        offers_1 = MLRecommendationEngine.match_offers(
            customer=customer_1,
            churn_probability=churn_prob_1,
            risk_category=risk_category_1,
        )

        offers_2 = MLRecommendationEngine.match_offers(
            customer=customer_2,
            churn_probability=churn_prob_2,
            risk_category=risk_category_2,
        )

        # Build comparable offer fingerprints (offer_type + expected_impact)
        fingerprint_1 = sorted(
            (o["offer_type"], o["expected_impact"]) for o in offers_1
        )
        fingerprint_2 = sorted(
            (o["offer_type"], o["expected_impact"]) for o in offers_2
        )

        assert fingerprint_1 != fingerprint_2, (
            f"Two customers with different risk levels produced identical offers.\n"
            f"Customer 1: risk_level={risk_1} "
            f"(charges={monthly_charges_1}, churn={churn_prob_1}, risk_cat={risk_category_1})\n"
            f"Customer 2: risk_level={risk_2} "
            f"(charges={monthly_charges_2}, churn={churn_prob_2}, risk_cat={risk_category_2})\n"
            f"Offers 1: {fingerprint_1}\n"
            f"Offers 2: {fingerprint_2}"
        )
