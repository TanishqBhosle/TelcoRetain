"""Admin API Router."""

import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_db, require_role
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_repo import UserRepository
from app.schemas.admin import SystemHealthResponse
from app.schemas.common import APIResponse
from app.schemas.users import UserResponse, UserUpdateRequest
from app.services.admin_service import AdminService
from app.services.user_service import UserService

router = APIRouter(tags=["Admin"])

ADMIN_ROLES = ["Super Admin", "Admin"]


async def get_admin_service(db=Depends(get_db)) -> AdminService:
    return AdminService(AuditRepository(db))


async def get_user_service(db=Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.get("/admin/system-health", response_model=APIResponse[SystemHealthResponse])
async def system_health(
    service: AdminService = Depends(get_admin_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    return APIResponse(success=True, message="System health retrieved", data=await service.get_system_health())


@router.get("/admin/users", response_model=APIResponse[List[UserResponse]])
async def list_users(
    service: UserService = Depends(get_user_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    users = await service.list_users()
    return APIResponse(success=True, message="Users retrieved", data=[UserResponse.model_validate(item) for item in users])


@router.get("/admin/users/{id}", response_model=APIResponse[UserResponse])
async def get_user(
    id: uuid.UUID,
    service: UserService = Depends(get_user_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    user = await service.get_user(id)
    return APIResponse(success=True, message="User retrieved", data=UserResponse.model_validate(user))


@router.post("/admin/users/{id}", response_model=APIResponse[UserResponse])
async def update_user(
    id: uuid.UUID,
    payload: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    user = await service.update_user(id, payload)
    return APIResponse(success=True, message="User updated", data=UserResponse.model_validate(user))


@router.delete("/admin/users/{id}", response_model=APIResponse[None])
async def delete_user(
    id: uuid.UUID,
    service: UserService = Depends(get_user_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    await service.delete_user(id)
    return APIResponse(success=True, message="User deleted", data=None)
