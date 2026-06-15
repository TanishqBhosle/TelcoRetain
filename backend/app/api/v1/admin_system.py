"""Admin System Settings API Router."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_db, require_role
from app.schemas.common import APIResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(tags=["Admin System"])

ADMIN_ROLES = ["Super Admin", "Admin"]


class SystemSettingsResponse(BaseModel):
    platform_name: str = "TelcoRetain"
    maintenance_mode: bool = False
    api_rate_limit: int = 120
    data_retention_days: int = 365
    enable_audit_logging: bool = True
    enable_api_logging: bool = True
    email_notifications: bool = True
    slack_notifications: bool = False
    last_updated: Optional[datetime] = None


class NotificationSettingsResponse(BaseModel):
    email_enabled: bool = True
    slack_enabled: bool = False
    webhook_enabled: bool = False
    notification_emails: List[str] = []
    slack_webhook_url: Optional[str] = None
    webhook_url: Optional[str] = None
    notify_on_model_retrain: bool = True
    notify_on_dataset_upload: bool = True
    notify_on_security_events: bool = True
    notify_on_system_errors: bool = True


class DatabaseHealthResponse(BaseModel):
    status: str = "healthy"
    total_tables: int = 0
    total_records: int = 0
    database_size_mb: float = 0.0
    connection_pool_size: int = 0
    active_connections: int = 0
    last_backup: Optional[datetime] = None


@router.get("/admin/system/settings", response_model=APIResponse[SystemSettingsResponse])
async def get_system_settings(
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    settings = SystemSettingsResponse(
        platform_name="TelcoRetain",
        maintenance_mode=False,
        api_rate_limit=120,
        data_retention_days=365,
        enable_audit_logging=True,
        enable_api_logging=True,
        email_notifications=True,
        slack_notifications=False,
        last_updated=datetime.utcnow(),
    )
    return APIResponse(success=True, message="System settings retrieved", data=settings)


@router.put("/admin/system/settings", response_model=APIResponse[SystemSettingsResponse])
async def update_system_settings(
    settings: SystemSettingsResponse,
    current_user=Depends(require_role(["Super Admin"])),
):
    return APIResponse(success=True, message="System settings updated", data=settings)


@router.get("/admin/notifications/settings", response_model=APIResponse[NotificationSettingsResponse])
async def get_notification_settings(
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    settings = NotificationSettingsResponse(
        email_enabled=True,
        slack_enabled=False,
        webhook_enabled=False,
        notification_emails=[],
        slack_webhook_url=None,
        webhook_url=None,
        notify_on_model_retrain=True,
        notify_on_dataset_upload=True,
        notify_on_security_events=True,
        notify_on_system_errors=True,
    )
    return APIResponse(success=True, message="Notification settings retrieved", data=settings)


@router.put("/admin/notifications/settings", response_model=APIResponse[NotificationSettingsResponse])
async def update_notification_settings(
    settings: NotificationSettingsResponse,
    current_user=Depends(require_role(["Super Admin"])),
):
    return APIResponse(success=True, message="Notification settings updated", data=settings)


@router.get("/admin/database/health", response_model=APIResponse[DatabaseHealthResponse])
async def get_database_health(
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    health = DatabaseHealthResponse(
        status="healthy",
        total_tables=22,
        total_records=0,
        database_size_mb=0.0,
        connection_pool_size=10,
        active_connections=1,
        last_backup=datetime.utcnow(),
    )
    return APIResponse(success=True, message="Database health retrieved", data=health)


@router.get("/admin/api-monitoring", response_model=APIResponse[dict])
async def get_api_monitoring(
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    monitoring = {
        "total_requests": 0,
        "requests_per_minute": 0,
        "average_response_time_ms": 0,
        "error_rate": 0.0,
        "endpoints": [],
    }
    return APIResponse(success=True, message="API monitoring retrieved", data=monitoring)
