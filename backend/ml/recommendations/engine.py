"""Rule-based retention offer matcher."""

from decimal import Decimal
from typing import Any, Dict, List


class MLRecommendationEngine:
    @staticmethod
    def match_offers(customer: Any, churn_probability: float, risk_category: str) -> List[Dict[str, Any]]:
        arpu = getattr(customer, "arpu", None) or Decimal("0")
        high_value = arpu >= Decimal("500")

        offers = []
        if risk_category == "HIGH" or churn_probability >= 0.7:
            offers.append({
                "offer_type": "discount",
                "description": "Targeted bill discount for high-risk retention.",
                "validity_days": 14,
                "expected_impact": "HIGH",
                "score": 0.9,
                "priority": 100,
            })
        if high_value:
            offers.append({
                "offer_type": "plan_upgrade",
                "description": "Loyalty plan upgrade with premium support.",
                "validity_days": 30,
                "expected_impact": "MEDIUM",
                "score": 0.75,
                "priority": 80,
            })
        offers.append({
            "offer_type": "data_bonus",
            "description": "Bonus data pack to reinforce product value.",
            "validity_days": 21,
            "expected_impact": "MEDIUM",
            "score": 0.6,
            "priority": 50,
        })
        return offers
