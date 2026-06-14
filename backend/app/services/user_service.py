"""
User Service.
"""

import uuid
from typing import List, Optional

from app.exceptions.custom import NotFoundError
from app.models.users import User
from app.repositories.user_repo import UserRepository
from app.schemas.users import UserUpdateRequest


class UserService:
    """Provides methods for user management operations."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def get_user(self, user_id: uuid.UUID) -> User:
        """Fetch user profile by UUID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")
        return user

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Fetch all platform users."""
        return await self.user_repo.list_users(skip, limit)

    async def update_user(self, user_id: uuid.UUID, req: UserUpdateRequest) -> User:
        """Update existing user properties or role mapping."""
        user = await self.get_user(user_id)

        if req.full_name is not None:
            user.full_name = req.full_name
        if req.gender is not None:
            user.gender = req.gender
        if req.is_active is not None:
            user.is_active = req.is_active

        if req.role_name is not None:
            role = await self.user_repo.get_role_by_name(req.role_name)
            if not role:
                raise NotFoundError(f"Role '{req.role_name}' not found")
            user.role_id = role.id

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Permanently delete user profile."""
        user = await self.get_user(user_id)
        await self.user_repo.delete(user)
