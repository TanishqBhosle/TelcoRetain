"""Audit and API logs router."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_user, get_db
from app.repositories.audit_repo import AuditRepository
from app.schemas.admin import ApiLogResponse, AuditLogResponse
from app.schemas.common import APIResponse, PaginatedData
from app.services.admin_service import AdminService

router = APIRouter(tags=["Audit"])


async def get_admin_service(db=Depends(get_db)) -> AdminService:
    return AdminService(AuditRepository(db))


@router.get("/admin/audit-logs", response_model=APIResponse[PaginatedData[AuditLogResponse]])
async def audit_logs(
    user_id: Optional[uuid.UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    service: AdminService = Depends(get_admin_service),
    current_user=Depends(get_current_user),
):
    items, total = await service.list_audit_logs(user_uuid=user_id, action=action, resource_type=resource_type, page=page, limit=limit)
    data = PaginatedData(items=items, total=total, page=page, limit=limit, pages=(total + limit - 1) // limit)
    return APIResponse(success=True, message="Audit logs retrieved", data=data)


@router.get("/admin/api-logs", response_model=APIResponse[List[ApiLogResponse]])
async def api_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=200),
    service: AdminService = Depends(get_admin_service),
    current_user=Depends(get_current_user),
):
    return APIResponse(success=True, message="API logs retrieved", data=await service.list_api_logs(page=page, limit=limit))
