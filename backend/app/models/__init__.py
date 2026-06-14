"""
Import all SQLAlchemy models so Alembic can detect them.
"""
from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.users import Role, Permission, RolePermission, User
from app.models.customers import (
    TelecomCustomer,
    RechargeHistory,
    UsageMetrics,
    NetworkQuality,
    CustomerSupport,
    PlanChangeHistory,
)
from app.models.ml import MLModel, ChurnPrediction, ChurnExplanation
from app.models.recommendations import RetentionRecommendation
from app.models.campaigns import Campaign, CampaignTarget, CampaignResult
from app.models.datasets import Dataset, DatasetVersion
from app.models.audit import AuditLog, ApiLog, ModelPerformanceLog

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Role",
    "Permission",
    "RolePermission",
    "User",
    "TelecomCustomer",
    "RechargeHistory",
    "UsageMetrics",
    "NetworkQuality",
    "CustomerSupport",
    "PlanChangeHistory",
    "MLModel",
    "ChurnPrediction",
    "ChurnExplanation",
    "RetentionRecommendation",
    "Campaign",
    "CampaignTarget",
    "CampaignResult",
    "Dataset",
    "DatasetVersion",
    "AuditLog",
    "ApiLog",
    "ModelPerformanceLog",
]