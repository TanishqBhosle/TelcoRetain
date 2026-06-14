"""
Usage Metrics Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customers import UsageMetrics


class UsageMetricsRepository:
    """Handles monthly usage records for customers."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_customer_id(self, customer_id: uuid.UUID) -> List[UsageMetrics]:
        """Fetch all monthly usage logs for a customer sorted chronologically."""
        stmt = (
            select(UsageMetrics)
            .where(UsageMetrics.customer_id == customer_id)
            .order_by(UsageMetrics.month.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_metrics(self, customer_id: uuid.UUID) -> Optional[UsageMetrics]:
        """Fetch the most recent month's usage logs for a customer."""
        stmt = (
            select(UsageMetrics)
            .where(UsageMetrics.customer_id == customer_id)
            .order_by(UsageMetrics.month.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, metrics: UsageMetrics) -> UsageMetrics:
        """Persist or update usage metrics month snapshot."""
        self.db.add(metrics)
        await self.db.commit()
        await self.db.refresh(metrics)
        return metrics
