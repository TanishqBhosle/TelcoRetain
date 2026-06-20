"""
Prediction Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# --- New IBM Telco-based request/response schemas ---


class PredictRequest(BaseModel):
    """Payload to request churn prediction with IBM Telco customer fields."""

    customer_id: Optional[uuid.UUID] = None
    gender: Optional[str] = None
    SeniorCitizen: Optional[int] = None
    Partner: Optional[str] = None
    Dependents: Optional[str] = None
    tenure: Optional[int] = None
    PhoneService: Optional[str] = None
    MultipleLines: Optional[str] = None
    InternetService: Optional[str] = None
    OnlineSecurity: Optional[str] = None
    OnlineBackup: Optional[str] = None
    DeviceProtection: Optional[str] = None
    TechSupport: Optional[str] = None
    StreamingTV: Optional[str] = None
    StreamingMovies: Optional[str] = None
    Contract: Optional[str] = None
    PaperlessBilling: Optional[str] = None
    PaymentMethod: Optional[str] = None
    MonthlyCharges: Optional[float] = None
    TotalCharges: Optional[float] = None


class ChurnDriver(BaseModel):
    """A single SHAP-based churn driver explanation."""

    feature_name: str
    shap_value: float
    feature_value: str
    direction: str  # increases_churn or decreases_churn
    rank: int


class RetentionOffer(BaseModel):
    """A single retention offer recommendation."""

    offer_type: str
    description: str
    validity_days: int
    expected_impact: str
    priority: int


class PredictionResponse(BaseModel):
    """Combined prediction result with explanations and recommendations."""

    churn_probability: float
    risk_category: str  # LOW, MEDIUM, HIGH
    confidence_score: float
    top_churn_drivers: List[ChurnDriver]
    recommendations: List[RetentionOffer]
    prediction_id: Optional[uuid.UUID] = None


# --- Legacy schemas kept for backward compatibility (bulk, history, etc.) ---


class LegacyPredictRequest(BaseModel):
    """Legacy payload requiring only a customer UUID (used by bulk/history endpoints)."""

    customer_id: uuid.UUID = Field(..., description="Internal UUID of the customer")


class BulkPredictRequest(BaseModel):
    """Payload to request churn predictions for multiple customers."""

    customer_ids: List[uuid.UUID] = Field(..., description="List of internal UUIDs of customers")


class LegacyPredictionResponse(BaseModel):
    """Legacy prediction response with DB-backed fields."""

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

    predictions: List[LegacyPredictionResponse]
    total_processed: int
    success_count: int
    failure_count: int
