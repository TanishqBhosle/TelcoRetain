"""
Recharge History Repository.
"""

import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customers import RechargeHistory


class RechargeHistoryRepository:
    """Handles persistence of customer recharge logs."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_customer_id(self, customer_id: uuid.UUID) -> List[RechargeHistory]:
        """Fetch all recharge histories for a customer."""
        stmt = (
            select(RechargeHistory)
            .where(RechargeHistory.customer_id == customer_id)
            .order_by(RechargeHistory.recharge_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self, record: RechargeHistory) -> RechargeHistory:
        """Persist a new recharge transaction."""
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
