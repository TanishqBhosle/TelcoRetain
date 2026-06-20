"""Rule-based retention offer generation."""

from typing import Any, Dict, List


class RecommendationEngine:
    """Rule-based retention offer generator using IBM Telco features."""

    @staticmethod
    def generate_offers(
        churn_probability: float,
        risk_category: str,
        customer_features: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Rule-based retention offer generation.

        Factors: churn_probability, contract_type, monthly_charges, tenure
        Returns offers sorted by priority score descending.
        Each offer: {offer_type, description, validity_days, expected_impact, priority}
        """
        contract_type = customer_features.get("Contract", "")
        monthly_charges = float(customer_features.get("MonthlyCharges", 0))
        tenure = int(customer_features.get("tenure", 0))

        offers: List[Dict[str, Any]] = []

        # HIGH risk (>=0.70): discount offer (priority 100)
        if risk_category == "HIGH" or churn_probability >= 0.70:
            offers.append({
                "offer_type": "discount",
                "description": "20% discount on monthly bill for 6 months",
                "validity_days": 180,
                "expected_impact": "high",
                "priority": 100,
            })

        # Month-to-month contract + HIGH risk: contract upgrade offer (priority 90)
        if contract_type == "Month-to-month" and (risk_category == "HIGH" or churn_probability >= 0.70):
            offers.append({
                "offer_type": "contract_upgrade",
                "description": "Upgrade to 1-year contract with 15% discount",
                "validity_days": 30,
                "expected_impact": "high",
                "priority": 90,
            })

        # High monthly charges (>80) + MEDIUM or HIGH risk: loyalty plan (priority 80)
        if monthly_charges > 80 and risk_category in ("MEDIUM", "HIGH"):
            offers.append({
                "offer_type": "loyalty_plan",
                "description": "Premium loyalty plan with exclusive benefits",
                "validity_days": 90,
                "expected_impact": "medium",
                "priority": 80,
            })

        # Short tenure (<12 months): onboarding support offer (priority 70)
        if tenure < 12:
            offers.append({
                "offer_type": "onboarding_support",
                "description": "Dedicated onboarding specialist for 3 months",
                "validity_days": 90,
                "expected_impact": "medium",
                "priority": 70,
            })

        # Default (always include): data bonus offer (priority 50)
        offers.append({
            "offer_type": "data_bonus",
            "description": "5GB bonus data for 3 months",
            "validity_days": 90,
            "expected_impact": "low",
            "priority": 50,
        })

        # Sort by priority descending
        offers.sort(key=lambda x: x["priority"], reverse=True)

        return offers


# Backward-compatible alias for existing consumers (will be removed in task 9)
class MLRecommendationEngine:
    """Legacy compatibility wrapper. Use RecommendationEngine instead."""

    @staticmethod
    def match_offers(customer: object, churn_probability: float, risk_category: str) -> list:
        """Adapter: maps old interface to new generate_offers interface."""
        # Extract IBM Telco features from customer object if available
        customer_features: Dict[str, Any] = {}
        if hasattr(customer, "contract_type"):
            customer_features["Contract"] = getattr(customer, "contract_type", "")
        if hasattr(customer, "monthly_charges"):
            customer_features["MonthlyCharges"] = float(getattr(customer, "monthly_charges", 0))
        if hasattr(customer, "tenure"):
            customer_features["tenure"] = int(getattr(customer, "tenure", 0))

        offers = RecommendationEngine.generate_offers(
            churn_probability=churn_probability,
            risk_category=risk_category,
            customer_features=customer_features,
        )

        # Add legacy 'score' field expected by old consumers
        for offer in offers:
            if "score" not in offer:
                impact_to_score = {"high": 0.9, "medium": 0.75, "low": 0.6}
                offer["score"] = impact_to_score.get(offer.get("expected_impact", "low"), 0.6)

        return offers
