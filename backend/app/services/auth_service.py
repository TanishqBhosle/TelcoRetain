"""
Authentication Service.
"""

import datetime
from typing import Optional, Tuple
import uuid

from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    create_verification_token, create_password_reset_token, decode_token
)
from app.exceptions.custom import AuthenticationError, ConflictError, NotFoundError
from app.models.users import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.email_service import email_service


class AuthService:
    """Manages secure register/login flows, session validation, and account lockouts."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, req: RegisterRequest) -> User:
        """Register a new platform user with target role."""
        # Check existing user
        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise ConflictError(f"User with email '{req.email}' already exists")

        # Resolve role
        role = await self.user_repo.get_role_by_name(req.role_name)
        if not role:
            # Fallback to Analyst if role doesn't exist
            role = await self.user_repo.get_role_by_name("Analyst")
            if not role:
                raise NotFoundError(f"Role '{req.role_name}' not found")

        hashed_password = get_password_hash(req.password)
        verify_tok = create_verification_token(req.email)

        user = User(
            email=req.email,
            full_name=req.full_name,
            password_hash=hashed_password,
            gender=req.gender,
            role_id=role.id,
            is_active=True,
            email_verified=False,
            verification_token=verify_tok,
        )

        created_user = await self.user_repo.create(user)

        # Send verification email (non-blocking)
        await email_service.send_verification_email(req.email, verify_tok)

        return created_user

    async def login(self, req: LoginRequest) -> TokenResponse:
        """Authenticate user and return access/refresh tokens. Enforces lockouts."""
        user = await self.user_repo.get_by_email(req.email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Check account lockout
        if user.is_locked:
            lock_duration = user.locked_until - datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            minutes_remaining = int(lock_duration.total_seconds() / 60) + 1
            raise AuthenticationError(f"Account is locked. Try again in {minutes_remaining} minutes.")

        # Verify password
        if not verify_password(req.password, user.password_hash):
            # Increment failed attempts
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                # Lock account for 15 minutes
                user.locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            await self.user_repo.update(user)
            raise AuthenticationError("Invalid email or password")

        # Successful login: reset failed counters
        user.failed_login_count = 0
        user.locked_until = None
        user.last_login = datetime.datetime.utcnow()
        await self.user_repo.update(user)

        # Generate tokens
        access = create_access_token(subject=str(user.id), role=user.role.name)
        refresh = create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            token_type="Bearer",
            expires_in=30 * 60,  # 30 mins
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token using a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise AuthenticationError("Invalid token subject")
                
            user_uuid = uuid.UUID(user_id_str)
            user = await self.user_repo.get_by_id(user_uuid)
            
            if not user or not user.is_active or user.is_locked:
                raise AuthenticationError("User is inactive or locked")

            access = create_access_token(subject=str(user.id), role=user.role.name)
            new_refresh = create_refresh_token(subject=str(user.id))

            return TokenResponse(
                access_token=access,
                refresh_token=new_refresh,
                token_type="Bearer",
                expires_in=30 * 60,
            )
        except Exception as e:
            raise AuthenticationError(f"Refresh failed: {str(e)}")

    async def request_password_reset(self, email: str) -> str:
        """Generates reset token for user and sends reset email."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("No user registered with this email")

        reset_tok = create_password_reset_token(email)
        user.verification_token = reset_tok
        await self.user_repo.update(user)

        # Send password reset email (non-blocking)
        await email_service.send_password_reset_email(email, reset_tok)

        return reset_tok

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        """Reset password using verified token."""
        try:
            payload = decode_token(token)
            if payload.get("type") != "password_reset":
                raise AuthenticationError("Invalid token type")
            
            email = payload.get("sub")
            if not email:
                raise AuthenticationError("Invalid token subject")

            user = await self.user_repo.get_by_email(email)
            if not user or user.verification_token != token:
                raise AuthenticationError("Reset token is invalid or has expired")

            user.password_hash = get_password_hash(new_password)
            user.verification_token = None
            user.failed_login_count = 0
            user.locked_until = None
            await self.user_repo.update(user)
        except Exception as e:
            raise AuthenticationError(f"Password reset failed: {str(e)}")

    async def verify_email(self, token: str) -> None:
        """Verify user's email via token link."""
        try:
            payload = decode_token(token)
            if payload.get("type") != "email_verify":
                raise AuthenticationError("Invalid token type")
                
            email = payload.get("sub")
            if not email:
                raise AuthenticationError("Invalid token subject")

            user = await self.user_repo.get_by_email(email)
            if not user or user.verification_token != token:
                raise AuthenticationError("Verification link is invalid or expired")

            user.email_verified = True
            user.verification_token = None
            await self.user_repo.update(user)
        except Exception as e:
            raise AuthenticationError(f"Email verification failed: {str(e)}")
