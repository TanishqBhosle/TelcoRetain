"""Tests for customer service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import NotFoundError


@pytest.mark.asyncio
class TestCustomerService:
    """Tests for CustomerService methods."""

    @patch("app.services.customer_service.CustomerRepository")
    async def test_get_customer_success(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_customer = MagicMock()
        mock_customer.id = uuid.uuid4()
        mock_customer.full_name = "Test Customer"
        mock_repo.get_by_id.return_value = mock_customer

        from app.services.customer_service import CustomerService
        service = CustomerService(mock_repo)

        result = await service.get_customer(mock_customer.id)
        assert result.full_name == "Test Customer"

    @patch("app.services.customer_service.CustomerRepository")
    async def test_get_customer_not_found(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        from app.services.customer_service import CustomerService
        service = CustomerService(mock_repo)

        with pytest.raises(NotFoundError):
            await service.get_customer(uuid.uuid4())

    @patch("app.services.customer_service.CustomerRepository")
    async def test_list_customers(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.list_customers.return_value = ([MagicMock(), MagicMock()], 2)

        from app.services.customer_service import CustomerService
        service = CustomerService(mock_repo)

        items, total = await service.list_customers(page=1, limit=20)
        assert total == 2
        assert len(items) == 2

    @patch("app.services.customer_service.CustomerRepository")
    async def test_create_customer(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_created = MagicMock()
        mock_created.id = uuid.uuid4()
        mock_created.customer_id = "CUST001"
        mock_repo.create.return_value = mock_created

        from app.services.customer_service import CustomerService
        from app.schemas.customers import TelecomCustomerCreate
        service = CustomerService(mock_repo)

        payload = TelecomCustomerCreate(
            customer_id="CUST001",
            full_name="New Customer",
            email="new@test.com",
            phone_number="+1234567890",
            churn_status=False,
            status="active",
        )

        result = await service.create_customer(payload)
        assert result.customer_id == "CUST001"

    @patch("app.services.customer_service.CustomerRepository")
    async def test_get_customer_timeline(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_timeline.return_value = [
            {"event_date": "2024-01-15", "event_type": "JOINED", "title": "Onboarded", "details": "Joined platform", "status": "active"}
        ]

        from app.services.customer_service import CustomerService
        service = CustomerService(mock_repo)

        timeline = await service.get_customer_timeline(uuid.uuid4())
        assert len(timeline) == 1
        assert timeline[0]["event_type"] == "JOINED"
