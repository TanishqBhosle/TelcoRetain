"""
Prediction Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml import ChurnPrediction, ChurnExplanation, MLModel


class PredictionRepository:
    """Handles persistence of churn predictions and SHAP explainability variables."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: uuid.UUID) -> Optional[ChurnPrediction]:
        """Fetch details of a single churn prediction with explanations loaded."""
        stmt = (
            select(ChurnPrediction)
            .where(ChurnPrediction.id == pk)
            .options(
                selectinload(ChurnPrediction.explanations),
                selectinload(ChurnPrediction.model),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_prediction(self, customer_id: uuid.UUID) -> Optional[ChurnPrediction]:
        """Fetch the most recent prediction snapshot for a customer."""
        stmt = (
            select(ChurnPrediction)
            .where(ChurnPrediction.customer_id == customer_id)
            .order_by(ChurnPrediction.prediction_date.desc())
            .options(selectinload(ChurnPrediction.explanations))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, prediction: ChurnPrediction) -> ChurnPrediction:
        """Persist a new churn prediction score."""
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction

    async def save_explanations(self, explanations: List[ChurnExplanation]) -> None:
        """Bulk persist SHAP feature explanations."""
        self.db.add_all(explanations)
        await self.db.commit()

    async def get_explanations(self, prediction_id: uuid.UUID) -> List[ChurnExplanation]:
        """Fetch SHAP value entries for a specific prediction."""
        stmt = (
            select(ChurnExplanation)
            .where(ChurnExplanation.prediction_id == prediction_id)
            .order_by(desc(func.abs(ChurnExplanation.shap_value)))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_predictions(self, skip: int = 0, limit: int = 20) -> List[ChurnPrediction]:
        """Fetch recent prediction history logs."""
        stmt = (
            select(ChurnPrediction)
            .order_by(ChurnPrediction.prediction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
