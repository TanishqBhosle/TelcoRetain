"""
FastAPI Security & Database Dependencies.
"""

from typing import AsyncGenerator, List, Callable
from fastapi import Depends, Request

from app.core.database import AsyncSessionLocal
from app.exceptions.custom import AuthenticationError, AuthorizationError
from app.models.users import User


async def get_db() -> AsyncGenerator:
    """Yields a database session from connection pool."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(request: Request) -> User:
    """FastAPI Dependency: Fetches the authenticated user attached by AuthMiddleware."""
    user = getattr(request.state, "user", None)
    if not user:
        raise AuthenticationError("Not authenticated. Missing or invalid Authorization header.")
    return user


def require_role(allowed_roles: List[str]) -> Callable:
    """FastAPI Dependency: Verifies the authenticated user has an authorized role."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.name if current_user.role else None
        if not user_role or user_role not in allowed_roles:
            raise AuthorizationError(
                f"Unauthorized. Required role: one of {allowed_roles}. Found: '{user_role}'"
            )
        return current_user

    return role_checker
