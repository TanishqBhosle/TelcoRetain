"""Shared test fixtures."""

import asyncio
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.delete = AsyncMock()
    yield session


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    user.email_verified = True
    user.role = MagicMock()
    user.role.name = "Analyst"
    return user


@pytest.fixture
def mock_customer():
    customer = MagicMock()
    customer.id = uuid.uuid4()
    customer.customer_id = "CUST001"
    customer.full_name = "John Doe"
    customer.email = "john@example.com"
    customer.phone_number = "+1234567890"
    customer.region = "North"
    customer.operator = "TelcoCorp"
    customer.arpu = 450.0
    customer.monthly_charges = 79.99
    customer.total_charges = 3200.0
    customer.tenure_months = 24
    customer.churn_status = False
    customer.status = "active"
    customer.contract_type = "annual"
    customer.join_date = "2024-01-15"
    customer.recharge_history = []
    customer.usage_metrics = []
    customer.network_quality = []
    customer.support_tickets = []
    customer.plan_changes = []
    return customer


@pytest.fixture
def mock_prediction():
    pred = MagicMock()
    pred.id = uuid.uuid4()
    pred.customer_id = uuid.uuid4()
    pred.model_id = uuid.uuid4()
    pred.prediction_date = "2025-06-14T10:00:00"
    pred.churn_probability = 0.75
    pred.risk_score = 75
    pred.risk_category = "HIGH"
    pred.confidence_score = 0.85
    pred.features_used = {"tenure_months": 12, "arpu": 300}
    pred.explanations = []
    return pred
