"""Tests for auth service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.auth import LoginRequest, RegisterRequest, PasswordResetConfirm, PasswordResetRequest
from app.exceptions.custom import AuthenticationError, NotFoundError, ValidationError


@pytest.mark.asyncio
class TestAuthService:
    """Tests for AuthService methods."""

    @patch("app.services.auth_service.UserRepository")
    async def test_register_success(self, mock_user_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = None
        mock_repo.get_role_by_name.return_value = MagicMock(id=uuid.uuid4(), name="Analyst")
        mock_repo.create.return_value = MagicMock(
            id=uuid.uuid4(), email="new@test.com", full_name="New User",
            role=MagicMock(name="Analyst")
        )

        from app.services.auth_service import AuthService
        service = AuthService(mock_repo)

        payload = RegisterRequest(
            email="new@test.com",
            password="SecurePass123!",
            full_name="New User"
        )

        with patch("app.services.auth_service.get_password_hash", return_value="hashed"), \
             patch("app.services.auth_service.create_verification_token", return_value="token123"):
            user = await service.register(payload)

        assert user is not None
        mock_repo.create.assert_called_once()

    @patch("app.services.auth_service.UserRepository")
    async def test_register_duplicate_email(self, mock_user_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = MagicMock(email="existing@test.com")

        from app.services.auth_service import AuthService
        service = AuthService(mock_repo)

        payload = RegisterRequest(
            email="existing@test.com",
            password="SecurePass123!",
            full_name="Existing User"
        )

        with pytest.raises(ValidationError):
            await service.register(payload)

    @patch("app.services.auth_service.UserRepository")
    async def test_login_success(self, mock_user_repo_cls):
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@test.com"
        mock_user.is_active = True
        mock_user.locked_until = None
        mock_user.failed_login_count = 0
        mock_user.password_hash = "hashed"
        mock_user.role = MagicMock(name="Analyst")
        mock_repo.get_by_email.return_value = mock_user

        from app.services.auth_service import AuthService
        service = AuthService(mock_repo)

        payload = LoginRequest(email="test@test.com", password="password123")

        with patch("app.services.auth_service.verify_password", return_value=True), \
             patch("app.services.auth_service.create_access_token", return_value="access"), \
             patch("app.services.auth_service.create_refresh_token", return_value="refresh"):
            tokens = await service.login(payload)

        assert tokens.access_token == "access"
        assert tokens.refresh_token == "refresh"

    @patch("app.services.auth_service.UserRepository")
    async def test_login_wrong_password(self, mock_user_repo_cls):
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.is_active = True
        mock_user.locked_until = None
        mock_user.failed_login_count = 0
        mock_user.password_hash = "hashed"
        mock_repo.get_by_email.return_value = mock_user

        from app.services.auth_service import AuthService
        service = AuthService(mock_repo)

        payload = LoginRequest(email="test@test.com", password="wrongpassword")

        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(AuthenticationError):
                await service.login(payload)

    @patch("app.services.auth_service.UserRepository")
    async def test_login_user_not_found(self, mock_user_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = None

        from app.services.auth_service import AuthService
        service = AuthService(mock_repo)

        payload = LoginRequest(email="nonexistent@test.com", password="password123")

        with pytest.raises(AuthenticationError):
            await service.login(payload)
