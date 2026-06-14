"""
Audit & Logging Repository.
"""

import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, ApiLog


class AuditRepository:
    """Handles persistence and analytics for security audit logs and API transactions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_audit_log(self, log: AuditLog) -> AuditLog:
        """Persist user action audit log."""
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_audit_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AuditLog], int]:
        """Fetch audit logs with filters and pagination."""
        stmt = select(AuditLog)
        count_stmt = select(func.count(AuditLog.id))

        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action == action)
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)

        result_count = await self.db.execute(count_stmt)
        total = result_count.scalar() or 0

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def save_api_log(self, log: ApiLog) -> ApiLog:
        """Persist API request/response metadata log."""
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_api_logs(self, skip: int = 0, limit: int = 100) -> List[ApiLog]:
        """Fetch historical API transaction logs."""
        stmt = select(ApiLog).order_by(ApiLog.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
