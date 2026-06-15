"""Admin Security Center API Router."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_db, require_role
from app.schemas.common import APIResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(tags=["Admin Security"])

ADMIN_ROLES = ["Super Admin", "Admin"]


class SecuritySettingsResponse(BaseModel):
    password_min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    session_timeout_minutes: int = 30
    require_email_verification: bool = True
    enable_2fa: bool = False
    last_updated: Optional[datetime] = None


class SecurityAuditResponse(BaseModel):
    total_login_attempts: int = 0
    failed_login_attempts: int = 0
    locked_accounts: int = 0
    active_sessions: int = 0
    recent_security_events: list = []


@router.get("/admin/security/settings", response_model=APIResponse[SecuritySettingsResponse])
async def get_security_settings(
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    settings = SecuritySettingsResponse(
        password_min_length=8,
        require_uppercase=True,
        require_lowercase=True,
        require_numbers=True,
        require_special_chars=True,
        max_login_attempts=5,
        lockout_duration_minutes=15,
        session_timeout_minutes=30,
        require_email_verification=True,
        enable_2fa=False,
        last_updated=datetime.utcnow(),
    )
    return APIResponse(success=True, message="Security settings retrieved", data=settings)


@router.put("/admin/security/settings", response_model=APIResponse[SecuritySettingsResponse])
async def update_security_settings(
    settings: SecuritySettingsResponse,
    current_user=Depends(require_role(["Super Admin"])),
):
    return APIResponse(success=True, message="Security settings updated", data=settings)


@router.get("/admin/security/audit", response_model=APIResponse[SecurityAuditResponse])
async def get_security_audit(
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    audit = SecurityAuditResponse(
        total_login_attempts=0,
        failed_login_attempts=0,
        locked_accounts=0,
        active_sessions=0,
        recent_security_events=[],
    )
    return APIResponse(success=True, message="Security audit retrieved", data=audit)
