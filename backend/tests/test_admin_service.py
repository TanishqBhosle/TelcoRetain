"""Tests for admin service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
class TestAdminService:
    """Tests for AdminService methods."""

    @patch("app.services.admin_service.AuditRepository")
    async def test_list_audit_logs(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.list_audit_logs.return_value = ([MagicMock(), MagicMock()], 2)

        from app.services.admin_service import AdminService
        service = AdminService(mock_repo)

        items, total = await service.list_audit_logs(page=1, limit=50)
        assert total == 2
        assert len(items) == 2

    @patch("app.services.admin_service.AuditRepository")
    async def test_list_api_logs(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.list_api_logs.return_value = [MagicMock()]

        from app.services.admin_service import AdminService
        service = AdminService(mock_repo)

        result = await service.list_api_logs(page=1, limit=100)
        assert len(result) == 1

    @patch("app.services.admin_service.AuditRepository")
    @patch("app.services.admin_service.check_database_connection", new_callable=lambda: AsyncMock)
    @patch("app.services.admin_service.ModelRegistry")
    async def test_get_system_health(self, mock_registry, mock_db_check, mock_repo_cls):
        mock_registry.is_loaded.return_value = True
        mock_db_check.return_value = True

        from app.services.admin_service import AdminService
        service = AdminService(mock_repo_cls)

        health = await service.get_system_health()
        assert health is not None
