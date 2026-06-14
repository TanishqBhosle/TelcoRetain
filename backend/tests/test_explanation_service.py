"""Tests for explanation service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import NotFoundError


@pytest.mark.asyncio
class TestExplanationService:
    """Tests for ExplanationService methods."""

    @patch("app.services.explanation_service.PredictionRepository")
    async def test_get_prediction_explanation_not_found(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        from app.services.explanation_service import ExplanationService
        service = ExplanationService(mock_repo)

        with pytest.raises(NotFoundError):
            await service.get_prediction_explanation(uuid.uuid4())

    @patch("app.services.explanation_service.PredictionRepository")
    async def test_get_prediction_explanation_success(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_prediction = MagicMock()
        mock_prediction.id = uuid.uuid4()
        mock_prediction.explanations = [
            MagicMock(
                feature_name="tenure_months",
                shap_value=-0.15,
                feature_value=12,
                feature_importance_rank=1,
            )
        ]
        mock_repo.get_by_id.return_value = mock_prediction

        from app.services.explanation_service import ExplanationService
        service = ExplanationService(mock_repo)

        result = await service.get_prediction_explanation(mock_prediction.id)
        assert result is not None
