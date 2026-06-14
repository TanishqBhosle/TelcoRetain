"""
Recommendation Pydantic schemas.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class OfferGenerateRequest(BaseModel):
    """Payload to request/generate recommendations for a customer."""

    customer_id: uuid.UUID = Field(..., description="Internal customer UUID")


class RecommendationResponse(BaseModel):
    """Personalized customer retention offer."""

    id: uuid.UUID
    customer_id: uuid.UUID
    churn_prediction_id: Optional[uuid.UUID] = None
    offer_type: str = Field(..., description="Offer category (e.g. discount, data_bonus, plan_upgrade)")
    description: str = Field(..., description="Human-readable description of the offer")
    validity_days: int = Field(..., description="Number of days the offer remains valid")
    expected_impact: Optional[str] = Field(None, description="Expected retention impact: LOW, MEDIUM, HIGH")
    score: Optional[float] = Field(None, description="Model-assigned offer match score (0.0 to 1.0)")
    status: str = Field(..., description="Offer status: pending, sent, accepted, rejected, expired")
    priority: int = Field(0, description="Priority weight (higher is shown first)")
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationUpdate(BaseModel):
    """Payload to update recommendation status."""

    status: str = Field(..., pattern="^(pending|sent|accepted|rejected|expired)$", description="New status value")
