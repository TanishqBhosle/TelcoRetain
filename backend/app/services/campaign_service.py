"""
Campaign Service.
"""

import datetime
from decimal import Decimal
from typing import List, Tuple
import uuid

from app.exceptions.custom import CampaignNotFoundError, CustomerNotFoundError
from app.models.campaigns import Campaign, CampaignTarget, CampaignResult
from app.repositories.campaign_repo import CampaignRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.recommendation_repo import RecommendationRepository
from app.schemas.campaigns import CampaignCreate, CampaignUpdate, CampaignTargetUpdate, CampaignResultResponse


class CampaignService:
    """Manages marketing campaign definition templates, customer targets, and financial returns auditing."""

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        customer_repo: CustomerRepository,
        rec_repo: RecommendationRepository,
    ) -> None:
        self.campaign_repo = campaign_repo
        self.customer_repo = customer_repo
        self.rec_repo = rec_repo

    async def create_campaign(self, creator_uuid: uuid.UUID, req: CampaignCreate) -> Campaign:
        """Create a new retention campaign."""
        campaign = Campaign(
            name=req.name,
            description=req.description,
            campaign_type=req.campaign_type,
            offer_details=req.offer_details,
            start_date=req.start_date,
            end_date=req.end_date,
            target_segment=req.target_segment,
            budget=req.budget,
            expected_customers=req.expected_customers,
            creator_id=creator_uuid,
            is_active=True,
        )
        return await self.campaign_repo.create(campaign)

    async def update_campaign(self, campaign_uuid: uuid.UUID, req: CampaignUpdate) -> Campaign:
        """Update campaign configs."""
        campaign = await self.campaign_repo.get_by_id(campaign_uuid)
        if not campaign:
            raise CampaignNotFoundError(campaign_uuid)

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)

        return await self.campaign_repo.update(campaign)

    async def get_campaign(self, campaign_uuid: uuid.UUID) -> Campaign:
        """Fetch campaign details by internal UUID."""
        campaign = await self.campaign_repo.get_by_id(campaign_uuid)
        if not campaign:
            raise CampaignNotFoundError(campaign_uuid)
        return campaign

    async def list_campaigns(self, page: int = 1, limit: int = 20) -> List[Campaign]:
        """Fetch list of all campaigns."""
        skip = (page - 1) * limit
        return await self.campaign_repo.list_campaigns(skip, limit)

    async def add_target_customers(self, campaign_uuid: uuid.UUID, customer_uuids: List[uuid.UUID]) -> int:
        """Add target customer cohorts to a campaign."""
        campaign = await self.get_campaign(campaign_uuid)

        targets = []
        added_count = 0
        for cust_uuid in customer_uuids:
            # Check customer exists
            cust = await self.customer_repo.get_by_id(cust_uuid)
            if not cust:
                continue

            # Check if already targeted
            existing = await self.campaign_repo.get_target(campaign_uuid, cust_uuid)
            if existing:
                continue

            target = CampaignTarget(
                campaign_id=campaign_uuid,
                customer_id=cust_uuid,
                status="pending"
            )
            targets.append(target)
            added_count += 1

        if targets:
            await self.campaign_repo.add_targets(targets)
            campaign.actual_customers = (campaign.actual_customers or 0) + added_count
            await self.campaign_repo.update(campaign)

        return added_count

    async def get_campaign_targets(
        self, campaign_uuid: uuid.UUID, page: int = 1, limit: int = 100
    ) -> Tuple[List[CampaignTarget], int]:
        """Fetch targeted cohorts lists (paginated)."""
        await self.get_campaign(campaign_uuid)
        skip = (page - 1) * limit
        return await self.campaign_repo.get_targets(campaign_uuid, skip, limit)

    async def update_customer_response(
        self, campaign_uuid: uuid.UUID, customer_uuid: uuid.UUID, req: CampaignTargetUpdate
    ) -> CampaignTarget:
        """Update campaign outcome variables for a targeted customer."""
        target = await self.campaign_repo.get_target(campaign_uuid, customer_uuid)
        if not target:
            raise CustomerNotFoundError(f"Customer targeted mapping not found for customer {customer_uuid}")

        if req.status is not None:
            target.status = req.status
            if req.status == "responded":
                target.response_date = datetime.datetime.utcnow()

        if req.offer_accepted is not None:
            target.offer_accepted = req.offer_accepted
            if req.offer_accepted:
                # Also accept any active recommendations generated for this customer
                recs = await self.rec_repo.get_active_recommendations(customer_uuid)
                for rec in recs:
                    rec.status = "accepted"
                    await self.rec_repo.save(rec)

        updated_target = await self.campaign_repo.update_target(target)
        
        # Re-compute results metrics asynchronously or synchronously
        await self.compute_campaign_results(campaign_uuid)

        return updated_target

    async def compute_campaign_results(self, campaign_uuid: uuid.UUID) -> CampaignResult:
        """Calculate and update aggregated conversions, response rates, and ROI metrics."""
        campaign = await self.get_campaign(campaign_uuid)

        targets, total = await self.campaign_repo.get_targets(campaign_uuid, skip=0, limit=100000)

        responses = sum(1 for t in targets if t.status == "responded" or t.response_date is not None)
        conversions = sum(1 for t in targets if t.offer_accepted is True)

        # Revenue impact estimation: convertors * monthly ARPU * retention multiplier (e.g. 6 months)
        revenue_impact = Decimal("0.00")
        for target in targets:
            if target.offer_accepted:
                cust = await self.customer_repo.get_by_id(target.customer_id)
                if cust and cust.arpu:
                    revenue_impact += cust.arpu * 6  # assume 6 months retention

        cost = campaign.budget or Decimal("0.00")
        roi = 0.0
        if cost > 0:
            roi = float((revenue_impact - cost) / cost)

        # Check if result row already exists
        result_entry = None
        if campaign.results:
            result_entry = campaign.results[0]

        if not result_entry:
            result_entry = CampaignResult(campaign_id=campaign_uuid)

        result_entry.total_targets = total
        result_entry.responses = responses
        result_entry.conversions = conversions
        result_entry.revenue_impact = revenue_impact
        result_entry.cost = cost
        result_entry.roi = roi

        return await self.campaign_repo.save_result(result_entry)

    async def get_campaign_analytics(self, campaign_uuid: uuid.UUID) -> CampaignResultResponse:
        """Retrieve aggregated KPI performance reports for a campaign."""
        campaign = await self.get_campaign(campaign_uuid)
        
        if not campaign.results:
            # Calculate metrics on the fly if missing
            await self.compute_campaign_results(campaign_uuid)
            # Re-fetch campaign
            campaign = await self.campaign_repo.get_by_id(campaign_uuid)

        res = campaign.results[0]
        return CampaignResultResponse(
            id=res.id,
            campaign_id=res.campaign_id,
            total_targets=res.total_targets,
            responses=res.responses,
            conversions=res.conversions,
            revenue_impact=res.revenue_impact,
            cost=res.cost,
            roi=float(res.roi) if res.roi is not None else 0.0,
            completion_date=res.completion_date
        )
