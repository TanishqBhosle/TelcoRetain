"""
User Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User, Role


class UserRepository:
    """Handles persistence and DB logic for User and Role entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a single user with role and permissions loaded."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.role).selectinload(Role.role_permissions)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by unique email."""
        stmt = (
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.role).selectinload(Role.role_permissions)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Persist a new user."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return await self.get_by_id(user.id)

    async def update(self, user: User) -> User:
        """Update existing user database state."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return await self.get_by_id(user.id)

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Fetch all platform users with roles loaded."""
        stmt = (
            select(User)
            .options(selectinload(User.role))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, user: User) -> None:
        """Delete user account."""
        await self.db.delete(user)
        await self.db.commit()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Retrieve Role object by name identifier."""
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
