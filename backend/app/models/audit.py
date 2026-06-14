"""
Audit and Logging Models.
Tables:
  - audit_logs: User action audit trail
  - api_logs: API request/response logging
  - model_performance_logs: ML model performance tracking
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


class AuditLog(Base, TimestampMixin, UUIDMixin):
    """
    Audit log for user actions and system events.
    Records who did what and when.
    """
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True  # e.g., 'login', 'prediction_created', 'campaign_updated'
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True  # e.g., 'user', 'customer', 'prediction', 'campaign'
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    request_payload: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # Full request body (sanitized)
    response_status: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True  # IPv6 compatible
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    additional_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="audit_logs"
    )

    __table_args__ = (
        Index("ix_audit_logs_user_action", "user_id", "action"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_timestamp", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} user={self.user_id}>"


class ApiLog(Base, TimestampMixin, UUIDMixin):
    """
    API request/response logging.
    Captures detailed API traffic for debugging and monitoring.
    """
    __tablename__ = "api_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(
        String(500), nullable=False, index=True
    )
    method: Mapped[str] = mapped_column(
        String(10), nullable=False  # GET, POST, PUT, DELETE, etc.
    )
    request_headers: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    request_body: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    response_status: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    response_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="api_logs"
    )

    __table_args__ = (
        Index("ix_api_logs_endpoint_method", "endpoint", "method"),
        Index("ix_api_logs_response_status", "response_status"),
    )

    def __repr__(self) -> str:
        return f"<ApiLog id={self.id} endpoint={self.endpoint} status={self.response_status}>"


class ModelPerformanceLog(Base, TimestampMixin, UUIDMixin):
    """
    ML model performance tracking.
    Records metrics for model evaluation and monitoring.
    """
    __tablename__ = "model_performance_logs"

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ml_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evaluation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    accuracy: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    precision: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    recall: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    f1_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    auc_roc: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    sample_size: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    drift_detected: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Relationships
    model: Mapped["MLModel"] = relationship(
        "MLModel", back_populates="performance_logs"  # type: ignore[name-defined]
    )

    __table_args__ = (
        Index("ix_model_perf_model_date", "model_id", "evaluation_date"),
    )

    def __repr__(self) -> str:
        return f"<ModelPerformanceLog model={self.model_id} accuracy={self.accuracy}>"