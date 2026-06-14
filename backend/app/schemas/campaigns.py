"""
Campaign Pydantic schemas.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    """Base campaign attributes."""

    name: str = Field(..., min_length=2, max_length=200, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    campaign_type: str = Field("retention", description="Type of campaign: retention, upsell, winback")
    offer_details: Optional[Dict[str, Any]] = Field(None, description="Offer detail configuration payload")
    start_date: date = Field(..., description="Start date of campaign")
    end_date: date = Field(..., description="End date of campaign")
    target_segment: Optional[str] = Field("high_risk", description="Target customer segment")
    budget: Optional[Decimal] = Field(None, description="Allocated budget")
    expected_customers: Optional[int] = Field(None, description="Expected targets size")
    is_active: bool = True


class CampaignCreate(CampaignBase):
    """Payload to create a new campaign."""

    pass


class CampaignUpdate(BaseModel):
    """Payload to update an existing campaign."""

    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    offer_details: Optional[Dict[str, Any]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_segment: Optional[str] = None
    budget: Optional[Decimal] = None
    expected_customers: Optional[int] = None
    actual_customers: Optional[int] = None
    is_active: Optional[bool] = None


class CampaignResponse(CampaignBase):
    """Campaign summary details."""

    id: uuid.UUID
    actual_customers: Optional[int] = None
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignTargetResponse(BaseModel):
    """Represents a targeted customer inside a campaign."""

    id: uuid.UUID
    campaign_id: uuid.UUID
    customer_id: uuid.UUID
    target_date: datetime
    status: str = Field(..., description="Target status: pending, sent, delivered, responded")
    response_date: Optional[datetime] = None
    offer_accepted: Optional[bool] = None

    class Config:
        from_attributes = True


class CampaignTargetUpdate(BaseModel):
    """Payload to update target customer response."""

    status: Optional[str] = Field(None, pattern="^(pending|sent|delivered|responded)$")
    offer_accepted: Optional[bool] = None


class CampaignResultResponse(BaseModel):
    """Aggregated campaign outcome metrics."""

    id: uuid.UUID
    campaign_id: uuid.UUID
    total_targets: int
    responses: int
    conversions: int
    revenue_impact: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    roi: Optional[float] = None
    completion_date: datetime

    class Config:
        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    """Campaign details with target lists and results summary."""

    targets: List[CampaignTargetResponse] = []
    results: List[CampaignResultResponse] = []

    class Config:
        from_attributes = True
