"""Campaign API Router."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_user, get_db, require_role
from app.repositories.campaign_repo import CampaignRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.recommendation_repo import RecommendationRepository
from app.schemas.campaigns import (
    CampaignCreate,
    CampaignDetailResponse,
    CampaignResponse,
    CampaignResultResponse,
    CampaignUpdate,
)
from app.schemas.common import APIResponse
from app.services.campaign_service import CampaignService

router = APIRouter(tags=["Campaigns"])

CAMPAIGN_WRITE_ROLES = ["Super Admin", "Admin", "Retention Manager", "Marketing Manager"]
CAMPAIGN_READ_ROLES = ["Super Admin", "Admin", "Retention Manager", "Marketing Manager", "Business Analyst", "Executive Viewer"]


async def get_campaign_service(db=Depends(get_db)) -> CampaignService:
    return CampaignService(CampaignRepository(db), CustomerRepository(db), RecommendationRepository(db))


@router.post("/campaigns", response_model=APIResponse[CampaignResponse])
async def create_campaign(
    payload: CampaignCreate,
    service: CampaignService = Depends(get_campaign_service),
    current_user=Depends(require_role(CAMPAIGN_WRITE_ROLES)),
):
    campaign = await service.create_campaign(current_user.id, payload)
    return APIResponse(success=True, message="Campaign created", data=CampaignResponse.model_validate(campaign))


@router.get("/campaigns", response_model=APIResponse[List[CampaignResponse]])
async def list_campaigns(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: CampaignService = Depends(get_campaign_service),
    current_user=Depends(require_role(CAMPAIGN_READ_ROLES)),
):
    campaigns = await service.list_campaigns(page=page, limit=limit)
    return APIResponse(
        success=True,
        message="Campaigns retrieved",
        data=[CampaignResponse.model_validate(item) for item in campaigns],
    )


@router.get("/campaigns/{id}", response_model=APIResponse[CampaignDetailResponse])
async def campaign_detail(
    id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
    current_user=Depends(require_role(CAMPAIGN_READ_ROLES)),
):
    campaign = await service.get_campaign(id)
    return APIResponse(success=True, message="Campaign retrieved", data=CampaignDetailResponse.model_validate(campaign))


@router.put("/campaigns/{id}", response_model=APIResponse[CampaignResponse])
async def update_campaign(
    id: uuid.UUID,
    payload: CampaignUpdate,
    service: CampaignService = Depends(get_campaign_service),
    current_user=Depends(require_role(CAMPAIGN_WRITE_ROLES)),
):
    campaign = await service.update_campaign(id, payload)
    return APIResponse(success=True, message="Campaign updated", data=CampaignResponse.model_validate(campaign))


@router.get("/campaigns/{id}/analytics", response_model=APIResponse[CampaignResultResponse])
async def campaign_analytics(
    id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
    current_user=Depends(require_role(CAMPAIGN_READ_ROLES)),
):
    result = await service.get_campaign_analytics(id)
    return APIResponse(success=True, message="Campaign analytics retrieved", data=result)
