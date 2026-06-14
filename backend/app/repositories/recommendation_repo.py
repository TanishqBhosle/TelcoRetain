"""
Recommendation Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendations import RetentionRecommendation


class RecommendationRepository:
    """Handles persistence of personalized retention recommendations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: uuid.UUID) -> Optional[RetentionRecommendation]:
        """Fetch recommendation details by internal UUID."""
        stmt = select(RetentionRecommendation).where(RetentionRecommendation.id == pk)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_customer_id(self, customer_id: uuid.UUID) -> List[RetentionRecommendation]:
        """Fetch all recommendations generated for a customer."""
        stmt = (
            select(RetentionRecommendation)
            .where(RetentionRecommendation.customer_id == customer_id)
            .order_by(RetentionRecommendation.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_recommendations(self, customer_id: uuid.UUID) -> List[RetentionRecommendation]:
        """Fetch all pending/sent (not yet accepted/rejected/expired) offers for a customer."""
        stmt = (
            select(RetentionRecommendation)
            .where(
                RetentionRecommendation.customer_id == customer_id,
                RetentionRecommendation.status.in_(["pending", "sent"])
            )
            .order_by(RetentionRecommendation.priority.desc(), RetentionRecommendation.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self, rec: RetentionRecommendation) -> RetentionRecommendation:
        """Persist recommendation."""
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec
