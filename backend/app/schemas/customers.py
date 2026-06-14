"""
Customer Pydantic schemas.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class RechargeHistoryResponse(BaseModel):
    """Details of a customer recharge transaction."""

    id: uuid.UUID
    recharge_date: datetime
    amount: Decimal
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None

    class Config:
        from_attributes = True


class UsageMetricsResponse(BaseModel):
    """Details of customer usage for a specific month."""

    id: uuid.UUID
    month: date
    voice_minutes: Optional[int] = None
    data_gb: Optional[Decimal] = None
    sms_count: Optional[int] = None
    arpu: Optional[Decimal] = None
    recharge_frequency: Optional[int] = None
    call_drop_count: Optional[int] = None

    class Config:
        from_attributes = True


class NetworkQualityResponse(BaseModel):
    """Details of average daily network quality experienced by the customer."""

    id: uuid.UUID
    date: date
    signal_strength_avg: Optional[float] = None
    call_drop_rate: Optional[float] = None
    network_availability: Optional[float] = None
    latency_ms: Optional[int] = None

    class Config:
        from_attributes = True


class CustomerSupportResponse(BaseModel):
    """Details of a customer support/complaint ticket."""

    id: uuid.UUID
    ticket_date: datetime
    ticket_type: Optional[str] = None
    complaint_type: Optional[str] = None
    description: Optional[str] = None
    resolution_status: str
    resolution_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlanChangeHistoryResponse(BaseModel):
    """Details of a plan change event."""

    id: uuid.UUID
    change_date: datetime
    old_plan: Optional[str] = None
    new_plan: Optional[str] = None
    change_reason: Optional[str] = None
    charges_changed: bool

    class Config:
        from_attributes = True


class TelecomCustomerBase(BaseModel):
    """Base customer fields."""

    customer_id: str = Field(..., description="Unique telecom operator identifier (e.g. CUST12345)")
    full_name: str = Field(..., description="Full name of customer")
    email: Optional[EmailStr] = None
    phone_number: str = Field(..., description="Active phone number")
    gender: Optional[str] = None
    age: Optional[int] = None
    region: Optional[str] = None
    operator: Optional[str] = None
    join_date: Optional[datetime] = None
    contract_type: Optional[str] = None
    paperless_billing: bool = False
    payment_method: Optional[str] = None
    monthly_charges: Optional[Decimal] = None
    total_charges: Optional[Decimal] = None
    tenure_months: Optional[int] = None
    arpu: Optional[Decimal] = None
    churn_status: bool = False
    status: str = "active"


class TelecomCustomerCreate(TelecomCustomerBase):
    """Payload to create a customer."""

    pass


class TelecomCustomerUpdate(BaseModel):
    """Payload to update an existing customer."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    region: Optional[str] = None
    operator: Optional[str] = None
    contract_type: Optional[str] = None
    paperless_billing: Optional[bool] = None
    payment_method: Optional[str] = None
    monthly_charges: Optional[Decimal] = None
    total_charges: Optional[Decimal] = None
    tenure_months: Optional[int] = None
    arpu: Optional[Decimal] = None
    churn_status: Optional[bool] = None
    status: Optional[str] = None


class TelecomCustomerResponse(TelecomCustomerBase):
    """Customer summary response payload."""

    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class TelecomCustomerDetailResponse(TelecomCustomerResponse):
    """Comprehensive customer detail payload containing behavioral histories."""

    recharge_history: List[RechargeHistoryResponse] = []
    usage_metrics: List[UsageMetricsResponse] = []
    network_quality: List[NetworkQualityResponse] = []
    support_tickets: List[CustomerSupportResponse] = []
    plan_changes: List[PlanChangeHistoryResponse] = []

    class Config:
        from_attributes = True


class CustomerTimelineEvent(BaseModel):
    """Represents a unified timeline event for customer activity tracking."""

    event_date: datetime
    event_type: str = Field(..., description="Type of event: RECHARGE, TICKET, PLAN_CHANGE, PREDICTION, CAMPAIGN")
    title: str = Field(..., description="Short title describing what happened")
    details: Optional[str] = Field(None, description="Detailed text describing the event")
    status: Optional[str] = Field(None, description="Status code or descriptor")
