"""Tests for prediction service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import CustomerNotFoundError, ModelNotLoadedError, NotFoundError


@pytest.mark.asyncio
class TestPredictionService:
    """Tests for PredictionService methods."""

    @patch("app.services.prediction_service.SupportTicketRepository")
    @patch("app.services.prediction_service.NetworkQualityRepository")
    @patch("app.services.prediction_service.UsageMetricsRepository")
    @patch("app.services.prediction_service.ModelRepository")
    @patch("app.services.prediction_service.PredictionRepository")
    @patch("app.services.prediction_service.CustomerRepository")
    async def test_predict_single_no_active_model(
        self, mock_cust_repo, mock_pred_repo, mock_model_repo,
        mock_usage_repo, mock_network_repo, mock_support_repo
    ):
        mock_model_repo.get_active_model.return_value = None

        from app.services.prediction_service import PredictionService
        service = PredictionService(
            mock_cust_repo, mock_pred_repo, mock_model_repo,
            mock_usage_repo, mock_network_repo, mock_support_repo
        )

        with patch("app.services.prediction_service.ModelRegistry") as mock_registry:
            mock_registry.is_loaded.return_value = True
            with pytest.raises(ModelNotLoadedError):
                await service.predict_single(uuid.uuid4(), MagicMock())

    @patch("app.services.prediction_service.SupportTicketRepository")
    @patch("app.services.prediction_service.NetworkQualityRepository")
    @patch("app.services.prediction_service.UsageMetricsRepository")
    @patch("app.services.prediction_service.ModelRepository")
    @patch("app.services.prediction_service.PredictionRepository")
    @patch("app.services.prediction_service.CustomerRepository")
    async def test_predict_single_customer_not_found(
        self, mock_cust_repo, mock_pred_repo, mock_model_repo,
        mock_usage_repo, mock_network_repo, mock_support_repo
    ):
        mock_model = MagicMock()
        mock_model_repo.get_active_model.return_value = mock_model
        mock_cust_repo.get_by_id.return_value = None

        from app.services.prediction_service import PredictionService
        service = PredictionService(
            mock_cust_repo, mock_pred_repo, mock_model_repo,
            mock_usage_repo, mock_network_repo, mock_support_repo
        )

        with patch("app.services.prediction_service.ModelRegistry") as mock_registry:
            mock_registry.is_loaded.return_value = True
            with pytest.raises(CustomerNotFoundError):
                await service.predict_single(uuid.uuid4(), MagicMock())

    @patch("app.services.prediction_service.SupportTicketRepository")
    @patch("app.services.prediction_service.NetworkQualityRepository")
    @patch("app.services.prediction_service.UsageMetricsRepository")
    @patch("app.services.prediction_service.ModelRepository")
    @patch("app.services.prediction_service.PredictionRepository")
    @patch("app.services.prediction_service.CustomerRepository")
    async def test_get_prediction_not_found(
        self, mock_cust_repo, mock_pred_repo, mock_model_repo,
        mock_usage_repo, mock_network_repo, mock_support_repo
    ):
        mock_pred_repo.get_by_id.return_value = None

        from app.services.prediction_service import PredictionService
        service = PredictionService(
            mock_cust_repo, mock_pred_repo, mock_model_repo,
            mock_usage_repo, mock_network_repo, mock_support_repo
        )

        with pytest.raises(NotFoundError):
            await service.get_prediction(uuid.uuid4())

    @patch("app.services.prediction_service.SupportTicketRepository")
    @patch("app.services.prediction_service.NetworkQualityRepository")
    @patch("app.services.prediction_service.UsageMetricsRepository")
    @patch("app.services.prediction_service.ModelRepository")
    @patch("app.services.prediction_service.PredictionRepository")
    @patch("app.services.prediction_service.CustomerRepository")
    async def test_list_predictions(
        self, mock_cust_repo, mock_pred_repo, mock_model_repo,
        mock_usage_repo, mock_network_repo, mock_support_repo
    ):
        mock_pred_repo.list_predictions.return_value = [MagicMock(), MagicMock()]

        from app.services.prediction_service import PredictionService
        service = PredictionService(
            mock_cust_repo, mock_pred_repo, mock_model_repo,
            mock_usage_repo, mock_network_repo, mock_support_repo
        )

        result = await service.list_predictions(page=1, limit=20)
        assert len(result) == 2
