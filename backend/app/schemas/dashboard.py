"""
Dashboard & Analytics Pydantic schemas.
"""

import uuid
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DashboardKPIResponse(BaseModel):
    """Aggregate KPIs shown on main dashboard."""

    total_customers: int = Field(..., description="Total customers in master DB")
    active_customers: int = Field(..., description="Customers with active status")
    average_churn_probability: float = Field(..., description="Mean churn risk across active customers")
    revenue_at_risk: Decimal = Field(..., description="Aggregate ARPU of high-risk customers")
    active_campaigns_count: int = Field(..., description="Number of currently running campaigns")
    campaign_conversion_rate: float = Field(..., description="Ratio of accepted offers to target customers")


class ChurnTrendPoint(BaseModel):
    """Represents a data point in monthly churn trend analysis."""

    period: str = Field(..., description="Month identifier, e.g. '2026-01'")
    average_churn_probability: float = Field(..., description="Mean prediction value for that period")
    predicted_churn_count: int = Field(..., description="Count of customers classified as high risk")


class DashboardChurnTrendsResponse(BaseModel):
    """Monthly churn trends list payload."""

    trends: List[ChurnTrendPoint]


class RevenueRiskPoint(BaseModel):
    """Represents a customer contributing to revenue leakage risk."""

    customer_uuid: uuid.UUID
    customer_id: str
    full_name: str
    arpu: Decimal
    churn_probability: float
    risk_level: str
    revenue_at_risk: Decimal = Field(..., description="ARPU multiplied by churn probability")


class DashboardRevenueRiskResponse(BaseModel):
    """List of top customers contributing to revenue leakage risk."""

    high_risk_customers: List[RevenueRiskPoint]


class RegionalAnalysisPoint(BaseModel):
    """Outlines retention metrics for a particular geographical area."""

    region: str
    customer_count: int
    churn_count: int
    average_churn_probability: float
    revenue_at_risk: Decimal


class DashboardRegionalResponse(BaseModel):
    """Regional breakdown payload."""

    regions: List[RegionalAnalysisPoint]


class OperatorAnalysisPoint(BaseModel):
    """Compares metrics against rival operators or within internal divisions."""

    operator: str
    customer_count: int
    churn_count: int
    average_churn_probability: float
    revenue_at_risk: Decimal


class DashboardOperatorResponse(BaseModel):
    """Operator breakdown payload."""

    operators: List[OperatorAnalysisPoint]
