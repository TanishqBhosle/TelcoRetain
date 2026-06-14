"""
Recommendation Service.
"""

import uuid
from typing import List

from app.exceptions.custom import CustomerNotFoundError, NotFoundError
from app.models.recommendations import RetentionRecommendation
from app.repositories.customer_repo import CustomerRepository
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.recommendation_repo import RecommendationRepository
from app.schemas.recommendations import RecommendationUpdate

# We will import the hybrid rules matching recommendation engine
from ml.recommendations.engine import MLRecommendationEngine


class RecommendationService:
    """Orchestrates retention offer matches based on customer usage and model risk indicators."""

    def __init__(
        self,
        customer_repo: CustomerRepository,
        prediction_repo: PredictionRepository,
        rec_repo: RecommendationRepository,
    ) -> None:
        self.customer_repo = customer_repo
        self.prediction_repo = prediction_repo
        self.rec_repo = rec_repo

    async def generate_recommendations(self, customer_uuid: uuid.UUID) -> List[RetentionRecommendation]:
        """Generates retention offers for customer and saves them to DB."""
        customer = await self.customer_repo.get_by_id(customer_uuid)
        if not customer:
            raise CustomerNotFoundError(customer_uuid)

        # Retrieve the latest churn prediction
        latest_pred = await self.prediction_repo.get_latest_prediction(customer_uuid)
        churn_prob = float(latest_pred.churn_probability) if latest_pred else 0.15
        risk_category = latest_pred.risk_category if latest_pred else "LOW"

        # Generate offers from hybrid engine
        offers = MLRecommendationEngine.match_offers(
            customer=customer,
            churn_probability=churn_prob,
            risk_category=risk_category
        )

        saved_recs = []
        for offer in offers:
            rec = RetentionRecommendation(
                customer_id=customer_uuid,
                churn_prediction_id=latest_pred.id if latest_pred else None,
                offer_type=offer["offer_type"],
                description=offer["description"],
                validity_days=offer["validity_days"],
                expected_impact=offer["expected_impact"],
                score=offer["score"],
                priority=offer["priority"],
                status="pending"
            )
            saved_rec = await self.rec_repo.save(rec)
            saved_recs.append(saved_rec)

        return saved_recs

    async def get_customer_recommendations(self, customer_uuid: uuid.UUID) -> List[RetentionRecommendation]:
        """Fetch all recommendations generated for a customer."""
        return await self.rec_repo.get_by_customer_id(customer_uuid)

    async def get_active_recommendations(self, customer_uuid: uuid.UUID) -> List[RetentionRecommendation]:
        """Fetch current pending offers."""
        return await self.rec_repo.get_active_recommendations(customer_uuid)

    async def update_recommendation_status(
        self, rec_uuid: uuid.UUID, req: RecommendationUpdate
    ) -> RetentionRecommendation:
        """Update recommendation action status (e.g. accepted, rejected)."""
        rec = await self.rec_repo.get_by_id(rec_uuid)
        if not rec:
            raise NotFoundError(f"Recommendation with ID '{rec_uuid}' not found")

        rec.status = req.status
        return await self.rec_repo.save(rec)
