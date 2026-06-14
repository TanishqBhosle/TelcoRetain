"""
User Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class PermissionResponse(BaseModel):
    """Details of a granular system permission."""

    id: uuid.UUID
    permission_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Details of a system role."""

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User profile response payload."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    gender: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Payload to update an existing user."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    gender: Optional[str] = None
    is_active: Optional[bool] = None
    role_name: Optional[str] = None
