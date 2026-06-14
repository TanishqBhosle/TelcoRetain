"""
Explanation Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FeatureExplanationResponse(BaseModel):
    """Indicates how much a single feature contributed to the churn score."""

    id: uuid.UUID
    feature_name: str = Field(..., description="Name of the customer feature")
    shap_value: float = Field(..., description="SHAP value (positive increases churn risk, negative reduces it)")
    feature_value: Optional[str] = Field(None, description="Actual value of the feature at prediction time")
    feature_importance_rank: Optional[int] = Field(None, description="Importance rank relative to other features")

    class Config:
        from_attributes = True


class ChurnExplanationResponse(BaseModel):
    """Aggregated SHAP explanation for a single prediction."""

    prediction_id: uuid.UUID
    model_id: uuid.UUID
    explanation_date: datetime
    features: List[FeatureExplanationResponse] = Field(..., description="All feature contributions")
    top_drivers: List[FeatureExplanationResponse] = Field(..., description="Subset of features with the strongest absolute contribution")
    reasons: List[str] = Field(..., description="Human-friendly text reasons explaining the churn triggers")
