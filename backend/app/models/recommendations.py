"""
Retention Recommendation Models.
Tables:
  - retention_recommendations: Personalized retention offers for customers at risk
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, Date, ForeignKey, Integer, String, Text, Numeric,
    Enum, UniqueConstraint, Index, func,
)
from app.models.types import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class RetentionRecommendation(Base, TimestampMixin, UUIDMixin):
    """
    Personalized retention recommendations for customers.
    Combines rule-based logic with ML scores to generate offers.
    """
    __tablename__ = "retention_recommendations"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    churn_prediction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("churn_predictions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    offer_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True  # e.g., 'discount', 'plan_upgrade', 'data_bonus'
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False  # Human-readable offer description
    )
    validity_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30  # How long the offer is valid
    )
    expected_impact: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True  # 'LOW', 'MEDIUM', 'HIGH' expected retention impact
    )
    score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True  # Recommendation score (0-1)
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True  # pending, sent, accepted, expired
    )
    priority: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0  # Higher priority = shown first to customer
    )

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="recommendations"
    )
    prediction: Mapped[Optional["ChurnPrediction"]] = relationship(
        "ChurnPrediction", back_populates="recommendations"  # type: ignore[name-defined]
    )

    __table_args__ = (
        Index("ix_retention_recs_customer_status", "customer_id", "status"),
        Index("ix_retention_recs_validity", "validity_days"),
    )

    def __repr__(self) -> str:
        return f"<RetentionRecommendation id={self.id} customer={self.customer_id} type={self.offer_type}>"