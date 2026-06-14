"""
Prediction Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Payload to request churn prediction for a customer."""

    customer_id: uuid.UUID = Field(..., description="Internal UUID of the customer")


class BulkPredictRequest(BaseModel):
    """Payload to request churn predictions for multiple customers."""

    customer_ids: List[uuid.UUID] = Field(..., description="List of internal UUIDs of customers")


class PredictionResponse(BaseModel):
    """Details of a single churn prediction result."""

    id: uuid.UUID
    customer_id: uuid.UUID
    model_id: uuid.UUID
    prediction_date: datetime
    churn_probability: float = Field(..., description="Probability of churn (0.0 to 1.0)")
    risk_score: int = Field(..., description="Integer score between 0 and 100")
    risk_category: str = Field(..., description="Risk tier: LOW, MEDIUM, HIGH")
    confidence_score: Optional[float] = Field(None, description="Model confidence level")
    features_used: Optional[Dict[str, Any]] = Field(None, description="Feature snapshot at prediction time")

    class Config:
        from_attributes = True


class BulkPredictionResponse(BaseModel):
    """Summary of batch prediction execution."""

    predictions: List[PredictionResponse]
    total_processed: int
    success_count: int
    failure_count: int
