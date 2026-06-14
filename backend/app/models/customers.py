"""
Customer Master Model and Customer Behavior Tables.
Tables:
  - telecom_customers (core customer data)
  - recharge_history (recharge records)
  - usage_metrics (monthly usage data)
  - network_quality (network metrics)
  - customer_support (support tickets)
  - plan_change_history (plan changes)
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, Date, ForeignKey, Integer, String, Text, Numeric,
    Float, UniqueConstraint, func, Index,
)
from app.models.types import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class TelecomCustomer(Base, TimestampMixin, UUIDMixin):
    """
    Core customer master data.
    Contains demographic and account information.
    """
    __tablename__ = "telecom_customers"

    customer_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    operator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    join_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    contract_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    paperless_billing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    monthly_charges: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    total_charges: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    tenure_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    arpu: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    churn_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    # Relationships
    recharge_history: Mapped[List["RechargeHistory"]] = relationship(
        "RechargeHistory", back_populates="customer", cascade="all, delete-orphan"
    )
    usage_metrics: Mapped[List["UsageMetrics"]] = relationship(
        "UsageMetrics", back_populates="customer", cascade="all, delete-orphan"
    )
    network_quality: Mapped[List["NetworkQuality"]] = relationship(
        "NetworkQuality", back_populates="customer", cascade="all, delete-orphan"
    )
    support_tickets: Mapped[List["CustomerSupport"]] = relationship(
        "CustomerSupport", back_populates="customer", cascade="all, delete-orphan"
    )
    plan_changes: Mapped[List["PlanChangeHistory"]] = relationship(
        "PlanChangeHistory", back_populates="customer", cascade="all, delete-orphan"
    )
    predictions: Mapped[List["ChurnPrediction"]] = relationship(
        "ChurnPrediction", back_populates="customer", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["RetentionRecommendation"]] = relationship(
        "RetentionRecommendation", back_populates="customer", cascade="all, delete-orphan"
    )
    campaign_targets: Mapped[List["CampaignTarget"]] = relationship(
        "CampaignTarget", back_populates="customer", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_telecom_customers_operator_region", "operator", "region"),
        Index("ix_telecom_customers_churn_status", "churn_status"),
        Index("ix_telecom_customers_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<TelecomCustomer id={self.customer_id} name={self.full_name}>"


class RechargeHistory(Base, TimestampMixin, UUIDMixin):
    """Customer recharge history records."""
    __tablename__ = "recharge_history"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recharge_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="recharge_history"
    )

    def __repr__(self) -> str:
        return f"<RechargeHistory customer={self.customer_id} amount={self.amount}>"


class UsageMetrics(Base, TimestampMixin, UUIDMixin):
    """Monthly usage metrics for customers."""
    __tablename__ = "usage_metrics"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month: Mapped[datetime] = mapped_column(
        Date, nullable=False, index=True
    )
    voice_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data_gb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    sms_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    arpu: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    recharge_frequency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    call_drop_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("customer_id", "month", name="uq_customer_month"),
    )

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="usage_metrics"
    )

    def __repr__(self) -> str:
        return f"<UsageMetrics customer={self.customer_id} month={self.month}>"


class NetworkQuality(Base, TimestampMixin, UUIDMixin):
    """Network quality metrics for customers."""
    __tablename__ = "network_quality"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    signal_strength_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    call_drop_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_availability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="network_quality"
    )

    def __repr__(self) -> str:
        return f"<NetworkQuality customer={self.customer_id} date={self.date}>"


class CustomerSupport(Base, TimestampMixin, UUIDMixin):
    """Customer support ticket history."""
    __tablename__ = "customer_support"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticket_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    ticket_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    complaint_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_status: Mapped[str] = mapped_column(
        String(30), default="open", nullable=False
    )
    resolution_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="support_tickets"
    )

    def __repr__(self) -> str:
        return f"<SupportTicket customer={self.customer_id} type={self.ticket_type}>"


class PlanChangeHistory(Base, TimestampMixin, UUIDMixin):
    """Customer plan change history."""
    __tablename__ = "plan_change_history"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telecom_customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    change_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    old_plan: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    new_plan: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    change_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    charges_changed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    customer: Mapped["TelecomCustomer"] = relationship(
        "TelecomCustomer", back_populates="plan_changes"
    )

    def __repr__(self) -> str:
        return f"<PlanChange customer={self.customer_id} old={self.old_plan} new={self.new_plan}>"