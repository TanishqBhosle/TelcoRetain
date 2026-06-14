"""
Authentication Pydantic schemas.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Payload to register a new user."""

    email: EmailStr = Field(..., description="Unique email address for the user")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    gender: Optional[str] = Field(None, description="Gender (e.g. Male, Female, Other)")
    role_name: str = Field("Analyst", description="Target role name (Admin, Analyst, Retention Manager, etc.)")


class LoginRequest(BaseModel):
    """Payload to authenticate a user."""

    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="User password")


class RefreshRequest(BaseModel):
    """Payload to refresh access token."""

    refresh_token: str = Field(..., description="Valid JWT refresh token")


class TokenResponse(BaseModel):
    """Response returned upon successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("Bearer", description="Token schema type")
    expires_in: int = Field(1800, description="Expiration time of access token in seconds")


class PasswordResetRequest(BaseModel):
    """Request password reset link."""

    email: EmailStr = Field(..., description="Registered user email")


class PasswordResetConfirm(BaseModel):
    """Confirm password reset payload."""

    token: str = Field(..., description="Verification reset token")
    new_password: str = Field(..., min_length=8, description="New user password")
