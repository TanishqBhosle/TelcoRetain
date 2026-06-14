"""
Machine Learning Model Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MLModelResponse(BaseModel):
    """Details of a registered ML model."""

    id: uuid.UUID
    name: str = Field(..., description="Unique model name")
    version: str = Field(..., description="Semantic version string")
    model_type: str = Field(..., description="Model algorithm type, e.g. xgboost, lightgbm")
    model_path: str = Field(..., description="Storage path to the model binary")
    feature_columns: List[str] = Field(..., description="List of feature names expected for inference")
    training_date: datetime
    accuracy: Optional[float] = None
    auc_score: Optional[float] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ModelPerformanceLogResponse(BaseModel):
    """Details of a model validation or evaluation run."""

    id: uuid.UUID
    model_id: uuid.UUID
    evaluation_date: datetime
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    sample_size: Optional[int] = None
    drift_detected: bool
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ModelRetrainRequest(BaseModel):
    """Payload to trigger asynchronous retraining on a dataset version."""

    dataset_version_id: Optional[uuid.UUID] = Field(None, description="Optional dataset version UUID to use for training")
