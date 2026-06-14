"""Tests for API endpoints."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_register_validation(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "password": "short",
            "full_name": ""
        })
        assert response.status_code in [400, 422]

    def test_login_validation(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@test.com",
            "password": ""
        })
        assert response.status_code in [400, 422]

    def test_me_without_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]


class TestCustomerEndpoints:
    """Tests for customer endpoints."""

    def test_list_customers_unauthorized(self, client):
        response = client.get("/api/v1/customers")
        assert response.status_code in [401, 403]

    def test_get_customer_unauthorized(self, client):
        response = client.get(f"/api/v1/customers/{uuid.uuid4()}")
        assert response.status_code in [401, 403]


class TestPredictionEndpoints:
    """Tests for prediction endpoints."""

    def test_predict_unauthorized(self, client):
        response = client.post("/api/v1/predictions/predict", json={
            "customer_id": str(uuid.uuid4())
        })
        assert response.status_code in [401, 403]

    def test_prediction_history_unauthorized(self, client):
        response = client.get("/api/v1/predictions/history")
        assert response.status_code in [401, 403]


class TestCampaignEndpoints:
    """Tests for campaign endpoints."""

    def test_list_campaigns_unauthorized(self, client):
        response = client.get("/api/v1/campaigns")
        assert response.status_code in [401, 403]


class TestModelEndpoints:
    """Tests for model endpoints."""

    def test_list_models_unauthorized(self, client):
        response = client.get("/api/v1/models")
        assert response.status_code in [401, 403]


class TestDatasetEndpoints:
    """Tests for dataset endpoints."""

    def test_list_datasets_unauthorized(self, client):
        response = client.get("/api/v1/datasets")
        assert response.status_code in [401, 403]
