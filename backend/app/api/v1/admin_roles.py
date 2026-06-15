"""Admin Roles & Permissions API Router."""

import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_db, require_role
from app.models.users import Permission, Role, RolePermission
from app.schemas.common import APIResponse
from app.schemas.users import PermissionResponse, RoleResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(tags=["Admin Roles"])

ADMIN_ROLES = ["Super Admin", "Admin"]


async def get_roles_with_permissions(db: AsyncSession) -> List[Role]:
    stmt = select(Role).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/admin/roles", response_model=APIResponse[List[RoleResponse]])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    roles = await get_roles_with_permissions(db)
    response = []
    for role in roles:
        permissions = [PermissionResponse.model_validate(rp.permission) for rp in role.role_permissions]
        response.append(RoleResponse(id=role.id, name=role.name, description=role.description, permissions=permissions))
    return APIResponse(success=True, message="Roles retrieved", data=response)


@router.post("/admin/roles", response_model=APIResponse[RoleResponse])
async def create_role(
    name: str,
    description: str = "",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["Super Admin"])),
):
    existing = await db.execute(select(Role).where(Role.name == name))
    if existing.scalar_one_or_none():
        from app.exceptions.custom import ValidationError
        raise ValidationError(f"Role '{name}' already exists")

    role = Role(name=name, description=description)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return APIResponse(success=True, message="Role created", data=RoleResponse(id=role.id, name=role.name, description=role.description, permissions=[]))


@router.put("/admin/roles/{id}", response_model=APIResponse[RoleResponse])
async def update_role(
    id: uuid.UUID,
    name: str = None,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["Super Admin"])),
):
    stmt = select(Role).where(Role.id == id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        from app.exceptions.custom import NotFoundError
        raise NotFoundError(f"Role with ID '{id}' not found")

    if name is not None:
        role.name = name
    if description is not None:
        role.description = description

    await db.commit()
    await db.refresh(role)
    return APIResponse(success=True, message="Role updated", data=RoleResponse(id=role.id, name=role.name, description=role.description, permissions=[]))


@router.delete("/admin/roles/{id}", response_model=APIResponse[None])
async def delete_role(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["Super Admin"])),
):
    stmt = select(Role).where(Role.id == id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        from app.exceptions.custom import NotFoundError
        raise NotFoundError(f"Role with ID '{id}' not found")

    await db.delete(role)
    await db.commit()
    return APIResponse(success=True, message="Role deleted", data=None)


@router.get("/admin/permissions", response_model=APIResponse[List[PermissionResponse]])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    stmt = select(Permission)
    result = await db.execute(stmt)
    permissions = list(result.scalars().all())
    return APIResponse(success=True, message="Permissions retrieved", data=[PermissionResponse.model_validate(p) for p in permissions])


@router.post("/admin/roles/{id}/permissions", response_model=APIResponse[RoleResponse])
async def assign_permissions_to_role(
    id: uuid.UUID,
    permission_ids: List[uuid.UUID],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["Super Admin"])),
):
    stmt = select(Role).where(Role.id == id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        from app.exceptions.custom import NotFoundError
        raise NotFoundError(f"Role with ID '{id}' not found")

    for perm_id in permission_ids:
        existing = await db.execute(
            select(RolePermission).where(RolePermission.role_id == id, RolePermission.permission_id == perm_id)
        )
        if not existing.scalar_one_or_none():
            db.add(RolePermission(role_id=id, permission_id=perm_id))

    await db.commit()
    updated_role = await db.execute(select(Role).where(Role.id == id))
    role = updated_role.scalar_one_or_none()
    return APIResponse(success=True, message="Permissions assigned", data=RoleResponse(id=role.id, name=role.name, description=role.description, permissions=[]))
