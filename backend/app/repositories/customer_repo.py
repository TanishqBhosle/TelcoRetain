"""
Customer Repository.
"""

import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customers import TelecomCustomer
from app.models.ml import ChurnPrediction


class CustomerRepository:
    """Handles database queries for TelecomCustomer master records."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: uuid.UUID) -> Optional[TelecomCustomer]:
        """Fetch customer by internal UUID primary key."""
        stmt = (
            select(TelecomCustomer)
            .where(TelecomCustomer.id == pk)
            .options(
                selectinload(TelecomCustomer.recharge_history),
                selectinload(TelecomCustomer.usage_metrics),
                selectinload(TelecomCustomer.network_quality),
                selectinload(TelecomCustomer.support_tickets),
                selectinload(TelecomCustomer.plan_changes),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_customer_id(self, customer_id: str) -> Optional[TelecomCustomer]:
        """Fetch customer by operator-assigned ID string (e.g. CUST001)."""
        stmt = (
            select(TelecomCustomer)
            .where(TelecomCustomer.customer_id == customer_id)
            .options(
                selectinload(TelecomCustomer.recharge_history),
                selectinload(TelecomCustomer.usage_metrics),
                selectinload(TelecomCustomer.network_quality),
                selectinload(TelecomCustomer.support_tickets),
                selectinload(TelecomCustomer.plan_changes),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, customer: TelecomCustomer) -> TelecomCustomer:
        """Persist a new customer master record."""
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update(self, customer: TelecomCustomer) -> TelecomCustomer:
        """Update existing customer master record."""
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 20,
        operator: Optional[str] = None,
        region: Optional[str] = None,
        risk_level: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TelecomCustomer], int]:
        """
        List customers with filters and pagination.
        Also returns total count of records matching search filter.
        """
        stmt = select(TelecomCustomer)
        count_stmt = select(func.count(TelecomCustomer.id))

        filters = []
        if operator:
            filters.append(TelecomCustomer.operator == operator)
        if region:
            filters.append(TelecomCustomer.region == region)
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    TelecomCustomer.full_name.ilike(search_pattern),
                    TelecomCustomer.customer_id.ilike(search_pattern),
                    TelecomCustomer.phone_number.ilike(search_pattern),
                    TelecomCustomer.email.ilike(search_pattern),
                )
            )

        if risk_level:
            # Subquery to fetch the latest prediction for each customer
            subq = (
                select(
                    ChurnPrediction.customer_id,
                    ChurnPrediction.risk_category,
                    func.row_number()
                    .over(
                        partition_by=ChurnPrediction.customer_id,
                        order_by=desc(ChurnPrediction.prediction_date),
                    )
                    .label("rn"),
                )
                .subquery()
            )
            stmt = stmt.join(subq, subq.c.customer_id == TelecomCustomer.id).where(
                and_(subq.c.rn == 1, subq.c.risk_category.ilike(risk_level))
            )
            count_stmt = count_stmt.join(subq, subq.c.customer_id == TelecomCustomer.id).where(
                and_(subq.c.rn == 1, subq.c.risk_category.ilike(risk_level))
            )

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        # Order by join date or full name by default
        stmt = stmt.order_by(TelecomCustomer.created_at.desc()).offset(skip).limit(limit)

        result_count = await self.db.execute(count_stmt)
        total = result_count.scalar() or 0

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_timeline(self, pk: uuid.UUID) -> List[dict]:
        """
        Gathers activity timeline for the customer.
        Returns a sorted list of chronological event dicts.
        """
        # Fetch customer with relations loaded
        customer = await self.get_by_id(pk)
        if not customer:
            return []

        events = []

        # 1. Join event
        if customer.join_date:
            events.append({
                "event_date": customer.join_date,
                "event_type": "JOINED",
                "title": "Onboarded to platform",
                "details": f"Joined under contract: {customer.contract_type or 'N/A'}",
                "status": customer.status,
            })

        # 2. Recharges
        for recharge in customer.recharge_history:
            events.append({
                "event_date": recharge.recharge_date,
                "event_type": "RECHARGE",
                "title": f"Recharged Account",
                "details": f"Amount: ${recharge.amount:.2f} via {recharge.payment_method or 'N/A'}",
                "status": "completed",
            })

        # 3. Tickets
        for ticket in customer.support_tickets:
            events.append({
                "event_date": ticket.ticket_date,
                "event_type": "SUPPORT_TICKET",
                "title": f"Support Ticket: {ticket.ticket_type or 'Issue'}",
                "details": f"[{ticket.complaint_type or 'General'}]: {ticket.description or 'No desc'}",
                "status": ticket.resolution_status,
            })

        # 4. Plan changes
        for pc in customer.plan_changes:
            events.append({
                "event_date": pc.change_date,
                "event_type": "PLAN_CHANGE",
                "title": "Plan Changed",
                "details": f"Upgraded/Downgraded from {pc.old_plan} to {pc.new_plan}. Reason: {pc.change_reason}",
                "status": "applied",
            })

        # Sort timeline events desc by date
        events.sort(key=lambda x: x["event_date"], reverse=True)
        return events
