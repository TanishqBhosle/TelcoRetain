"""
Campaign Management Models.
Tables:
  - campaigns: Retention campaign definitions
  - campaign_targets: Customer-campaign join table
  - campaign_results: Campaign execution results
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, Date, ForeignKey, Integer, String, Text, Numeric,
    UniqueConstraint, Index, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Campaign(Base, TimestampMixin, UUIDMixin):
    """
    Retention campaign definitions.
    Each campaign targets a segment of customers with specific offers.
    """
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    campaign_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # e.g., 'retention', 'upsell', 'winback'
    )
    offer_details: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # Offer configuration (discount %, free data, etc.)
    start_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    end_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    target_segment: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True  # e.g., 'high_risk', 'medium_risk', 'all'
    )
    budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    expected_customers: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    actual_customers: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_campaigns"
    )
    targets: Mapped[List["CampaignTarget"]] = relationship(
        "CampaignTarget", back_populates="campaign", cascade="all, delete-orphan"
    )
    results: Mapped[List["CampaignResult"]] = relationship(
        "CampaignResult", back_populates="campaign", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_campaigns_dates", "start_date", "end_date"),
        Index("ix_campaigns_type_active", "campaign_type", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Campaign id={self.id} name={self.name} type={self.campaign_type}>"


class CampaignTarget(Base, TimestampMixin, UUIDMixin):
    """
    Customer-campaign join table.
    Tracks which customers are targeted by which campaigns.
    """
    __tablename__ = "campaign_targets"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True  # pending, sent, delivered, responded
    )
    response_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    offer_accepted: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="targets"
    )
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="campaign_targets"
    )

    __table_args__ = (
        UniqueConstraint("campaign_id", "customer_id", name="uq_campaign_customer"),
        Index("ix_campaign_targets_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<CampaignTarget campaign={self.campaign_id} customer={self.customer_id}>"


class CampaignResult(Base, TimestampMixin, UUIDMixin):
    """
    Campaign execution results and metrics.
    Aggregated outcomes after campaign completion.
    """
    __tablename__ = "campaign_results"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_targets: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0  # Renamed from record_count per spec
    )
    responses: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    conversions: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    revenue_impact: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    roi: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 4), nullable=True
    )
    completion_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="results"
    )

    def __repr__(self) -> str:
        return f"<CampaignResult campaign={self.campaign_id} targets={self.total_targets}>"