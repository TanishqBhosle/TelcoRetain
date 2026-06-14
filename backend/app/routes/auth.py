"""
Authentication Router.
"""

from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_db, get_current_user
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshRequest, TokenResponse,
    PasswordResetRequest, PasswordResetConfirm
)
from app.schemas.users import UserResponse
from app.schemas.common import APIResponse
from app.core.security import blacklist_token

router = APIRouter(tags=["Authentication"])


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency: initializes AuthService."""
    return AuthService(UserRepository(db))


@router.post("/auth/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Registers a new platform user."""
    user = await auth_service.register(payload)
    return APIResponse(
        success=True,
        message="User registered successfully. Please verify your email.",
        data=UserResponse.model_validate(user),
    )


@router.post("/auth/login", response_model=APIResponse[TokenResponse])
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Authenticates user and returns JWT access & refresh tokens."""
    tokens = await auth_service.login(payload)
    return APIResponse(
        success=True,
        message="Login successful",
        data=tokens,
    )


@router.post("/auth/refresh", response_model=APIResponse[TokenResponse])
async def refresh(payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Issues a new JWT access/refresh token pair using a valid refresh token."""
    tokens = await auth_service.refresh_tokens(payload.refresh_token)
    return APIResponse(
        success=True,
        message="Tokens refreshed successfully",
        data=tokens,
    )


@router.post("/auth/logout", response_model=APIResponse[None])
async def logout(request: Request, current_user=Depends(get_current_user)):
    """Blacklists current access token and logs user out."""
    token = getattr(request.state, "token", None)
    if token:
        # Expire in 1 hour (3600 seconds)
        await blacklist_token(token, 3600)
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data=None,
    )


@router.get("/auth/me", response_model=APIResponse[UserResponse])
async def me(current_user=Depends(get_current_user)):
    """Fetches details of the currently logged-in user."""
    return APIResponse(
        success=True,
        message="Current user profile fetched",
        data=UserResponse.model_validate(current_user),
    )


@router.post("/auth/password-reset/request", response_model=APIResponse[str])
async def request_password_reset(payload: PasswordResetRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Generates a password reset token. In production, this would email the user."""
    token = await auth_service.request_password_reset(payload.email)
    return APIResponse(
        success=True,
        message="Password reset instructions generated.",
        data=token,
    )


@router.post("/auth/password-reset/confirm", response_model=APIResponse[None])
async def confirm_password_reset(payload: PasswordResetConfirm, auth_service: AuthService = Depends(get_auth_service)):
    """Resets user's password using the verified reset token."""
    await auth_service.confirm_password_reset(payload.token, payload.new_password)
    return APIResponse(
        success=True,
        message="Password has been reset successfully",
        data=None,
    )


@router.get("/auth/verify-email", response_model=APIResponse[None])
async def verify_email(token: str, auth_service: AuthService = Depends(get_auth_service)):
    """Verify email address using verification token."""
    await auth_service.verify_email(token)
    return APIResponse(
        success=True,
        message="Email verified successfully",
        data=None,
    )
