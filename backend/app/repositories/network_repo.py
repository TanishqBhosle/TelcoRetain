"""
Network Quality Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customers import NetworkQuality


class NetworkQualityRepository:
    """Handles network logs mapping daily signal latency metrics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_customer_id(self, customer_id: uuid.UUID) -> List[NetworkQuality]:
        """Fetch all network quality logs for a customer sorted chronologically."""
        stmt = (
            select(NetworkQuality)
            .where(NetworkQuality.customer_id == customer_id)
            .order_by(NetworkQuality.date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest(self, customer_id: uuid.UUID) -> Optional[NetworkQuality]:
        """Fetch the most recent daily network metrics for a customer."""
        stmt = (
            select(NetworkQuality)
            .where(NetworkQuality.customer_id == customer_id)
            .order_by(NetworkQuality.date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, record: NetworkQuality) -> NetworkQuality:
        """Persist daily quality log."""
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
