"""
Campaign Repository.
"""

import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaigns import Campaign, CampaignTarget, CampaignResult


class CampaignRepository:
    """Handles campaign configs, target customer mappings, and performance aggregates."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: uuid.UUID) -> Optional[Campaign]:
        """Fetch details of a single campaign."""
        stmt = (
            select(Campaign)
            .where(Campaign.id == pk)
            .options(
                selectinload(Campaign.targets),
                selectinload(Campaign.results),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, campaign: Campaign) -> Campaign:
        """Persist a new campaign configuration."""
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def update(self, campaign: Campaign) -> Campaign:
        """Update existing campaign database state."""
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def list_campaigns(self, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """List campaigns ordered by start date."""
        stmt = (
            select(Campaign)
            .order_by(Campaign.start_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_targets(self, targets: List[CampaignTarget]) -> None:
        """Bulk insert targeted customer cohorts into a campaign."""
        self.db.add_all(targets)
        await self.db.commit()

    async def get_target(self, campaign_id: uuid.UUID, customer_id: uuid.UUID) -> Optional[CampaignTarget]:
        """Fetch a specific campaign target join entry."""
        stmt = select(CampaignTarget).where(
            and_(
                CampaignTarget.campaign_id == campaign_id,
                CampaignTarget.customer_id == customer_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_target(self, target: CampaignTarget) -> CampaignTarget:
        """Update a campaign target state (e.g. conversion, offer response)."""
        self.db.add(target)
        await self.db.commit()
        await self.db.refresh(target)
        return target

    async def get_targets(
        self, campaign_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[CampaignTarget], int]:
        """List paginated customer cohorts assigned to a campaign."""
        stmt = (
            select(CampaignTarget)
            .where(CampaignTarget.campaign_id == campaign_id)
            .offset(skip)
            .limit(limit)
        )
        count_stmt = select(func.count(CampaignTarget.id)).where(CampaignTarget.campaign_id == campaign_id)

        result_count = await self.db.execute(count_stmt)
        total = result_count.scalar() or 0

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def get_active_campaigns_count(self) -> int:
        """Return total count of active/running campaigns."""
        stmt = select(func.count(Campaign.id)).where(Campaign.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def save_result(self, result_entry: CampaignResult) -> CampaignResult:
        """Persist/update aggregated campaign execution outcomes."""
        self.db.add(result_entry)
        await self.db.commit()
        await self.db.refresh(result_entry)
        return result_entry
