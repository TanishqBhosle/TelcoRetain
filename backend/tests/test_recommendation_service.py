"""Tests for recommendation service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import NotFoundError


@pytest.mark.asyncio
class TestRecommendationService:
    """Tests for RecommendationService methods."""

    @patch("app.services.recommendation_service.RecommendationRepository")
    @patch("app.services.recommendation_service.PredictionRepository")
    @patch("app.services.recommendation_service.CustomerRepository")
    async def test_generate_recommendations_customer_not_found(
        self, mock_cust_repo, mock_pred_repo, mock_rec_repo
    ):
        mock_cust_repo.get_by_id.return_value = None

        from app.services.recommendation_service import RecommendationService
        service = RecommendationService(mock_cust_repo, mock_pred_repo, mock_rec_repo)

        with pytest.raises(NotFoundError):
            await service.generate_recommendations(uuid.uuid4())

    @patch("app.services.recommendation_service.RecommendationRepository")
    @patch("app.services.recommendation_service.PredictionRepository")
    @patch("app.services.recommendation_service.CustomerRepository")
    async def test_get_customer_recommendations(
        self, mock_cust_repo, mock_pred_repo, mock_rec_repo
    ):
        mock_rec_repo.get_by_customer_id.return_value = [MagicMock(), MagicMock()]

        from app.services.recommendation_service import RecommendationService
        service = RecommendationService(mock_cust_repo, mock_pred_repo, mock_rec_repo)

        result = await service.get_customer_recommendations(uuid.uuid4())
        assert len(result) == 2
