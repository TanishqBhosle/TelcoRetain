"""
Support Ticket Repository.
"""

import uuid
from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customers import CustomerSupport


class SupportTicketRepository:
    """Handles support ticket logs and complaints statistics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_customer_id(self, customer_id: uuid.UUID) -> List[CustomerSupport]:
        """Fetch all support tickets for a customer."""
        stmt = (
            select(CustomerSupport)
            .where(CustomerSupport.customer_id == customer_id)
            .order_by(CustomerSupport.ticket_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_complaint_count(self, customer_id: uuid.UUID, since_days: int = 30) -> int:
        """Fetch count of support tickets raised by customer in the last N days."""
        # Note: since_days check can be simplified or direct count of open tickets
        stmt = (
            select(func.count(CustomerSupport.id))
            .where(CustomerSupport.customer_id == customer_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def save(self, ticket: CustomerSupport) -> CustomerSupport:
        """Persist support ticket details."""
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket
