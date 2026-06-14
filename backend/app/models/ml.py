"""
Machine Learning Models for Churn Prediction and Explainability.
Tables:
  - ml_models: Registry of trained ML models
  - churn_predictions: Prediction results for customers
  - churn_explanations: SHAP values and feature contributions per prediction
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, String, Text, Numeric,
    UniqueConstraint, Index, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class MLModel(Base, TimestampMixin, UUIDMixin):
    """
    Registry of trained ML models (XGBoost, LightGBM, etc.).
    Stores model metadata and artifact paths.
    """
    __tablename__ = "ml_models"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    model_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # e.g., 'xgboost', 'lightgbm', 'ensemble'
    )
    model_path: Mapped[str] = mapped_column(
        String(500), nullable=False  # Path to serialized model file
    )
    feature_columns: Mapped[List[str]] = mapped_column(
        JSONB, nullable=False  # List of feature names used in training
    )
    training_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    accuracy: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True  # Validation accuracy
    )
    auc_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True  # Validation AUC-ROC
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False  # Only one active model at a time
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    predictions: Mapped[List["ChurnPrediction"]] = relationship(
        "ChurnPrediction", back_populates="model", cascade="all, delete-orphan"
    )
    explanations: Mapped[List["ChurnExplanation"]] = relationship(
        "ChurnExplanation", back_populates="model", cascade="all, delete-orphan"
    )
    performance_logs: Mapped[List["ModelPerformanceLog"]] = relationship(
        "ModelPerformanceLog", back_populates="model", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_ml_models_is_active", "is_active"),
        UniqueConstraint("name", "version", name="uq_ml_model_name_version"),
    )

    def __repr__(self) -> str:
        return f"<MLModel id={self.id} name={self.name} version={self.version} type={self.model_type}>"


class ChurnPrediction(Base, TimestampMixin, UUIDMixin):
    """
    Churn prediction results for customers.
    Stores the probability scores and risk classifications.
    """
    __tablename__ = "churn_predictions"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ml_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    prediction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    churn_probability: Mapped[float] = mapped_column(
        Numeric(5, 4), nullable=False  # Probability between 0 and 1
    )
    risk_score: Mapped[int] = mapped_column(
        Integer, nullable=False  # Integer 0-100 representing risk percentage
    )
    risk_category: Mapped[str] = mapped_column(
        String(20), nullable=False  # 'LOW', 'MEDIUM', 'HIGH'
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True  # Model confidence in prediction
    )
    features_used: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True  # Snapshot of feature values at prediction time
    )

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="predictions"
    )
    model: Mapped["MLModel"] = relationship(
        "MLModel", back_populates="predictions"
    )
    explanations: Mapped[List["ChurnExplanation"]] = relationship(
        "ChurnExplanation", back_populates="prediction", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["RetentionRecommendation"]] = relationship(
        "RetentionRecommendation", back_populates="prediction", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_churn_predictions_customer_date", "customer_id", "prediction_date"),
        Index("ix_churn_predictions_risk_category", "risk_category"),
        Index("ix_churn_predictions_model_date", "model_id", "prediction_date"),
    )

    def __repr__(self) -> str:
        return f"<ChurnPrediction id={self.id} customer={self.customer_id} risk={self.risk_score}>"


class ChurnExplanation(Base, TimestampMixin, UUIDMixin):
    """
    SHAP explanations for individual predictions.
    Stores feature contributions and explanation metadata.
    """
    __tablename__ = "churn_explanations"

    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("churn_predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ml_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    feature_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    shap_value: Mapped[float] = mapped_column(
        Numeric(8, 6), nullable=False  # SHAP value for this feature
    )
    feature_value: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True  # Original feature value as string
    )
    feature_importance_rank: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True  # Rank by absolute SHAP value (1 = most important)
    )
    explanation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    prediction: Mapped["ChurnPrediction"] = relationship(
        "ChurnPrediction", back_populates="explanations"
    )
    model: Mapped["MLModel"] = relationship(
        "MLModel", back_populates="explanations"
    )

    __table_args__ = (
        Index("ix_churn_explanations_prediction_feature", "prediction_id", "feature_name"),
        Index("ix_churn_explanations_model_date", "model_id", "explanation_date"),
    )

    def __repr__(self) -> str:
        return f"<ChurnExplanation id={self.id} prediction={self.prediction_id} feature={self.feature_name}>"
