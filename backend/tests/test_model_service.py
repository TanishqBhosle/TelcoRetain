"""Tests for model service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import NotFoundError


@pytest.mark.asyncio
class TestModelService:
    """Tests for ModelService methods."""

    @patch("app.services.model_service.ModelRepository")
    async def test_get_model_success(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_model = MagicMock()
        mock_model.id = uuid.uuid4()
        mock_model.name = "test_model"
        mock_repo.get_by_id.return_value = mock_model

        from app.services.model_service import ModelService
        service = ModelService(mock_repo)

        result = await service.get_model(mock_model.id)
        assert result.name == "test_model"

    @patch("app.services.model_service.ModelRepository")
    async def test_get_model_not_found(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        from app.services.model_service import ModelService
        service = ModelService(mock_repo)

        with pytest.raises(NotFoundError):
            await service.get_model(uuid.uuid4())

    @patch("app.services.model_service.ModelRepository")
    async def test_list_models(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.list_models.return_value = [MagicMock(), MagicMock()]

        from app.services.model_service import ModelService
        service = ModelService(mock_repo)

        result = await service.list_models()
        assert len(result) == 2

    @patch("app.services.model_service.ModelRepository")
    async def test_activate_model(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_model = MagicMock()
        mock_model.id = uuid.uuid4()
        mock_repo.get_by_id.return_value = mock_model
        mock_repo.activate_model.return_value = mock_model

        from app.services.model_service import ModelService
        service = ModelService(mock_repo)

        result = await service.activate_model_version(mock_model.id)
        assert result is not None

    @patch("app.services.model_service.ModelRepository")
    async def test_add_performance_metrics(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_model = MagicMock()
        mock_model.id = uuid.uuid4()
        mock_repo.get_by_id.return_value = mock_model
        mock_log = MagicMock()
        mock_repo.save_performance_log.return_value = mock_log

        from app.services.model_service import ModelService
        service = ModelService(mock_repo)

        result = await service.add_performance_metrics(
            mock_model.id, accuracy=0.95, precision=0.93, recall=0.91,
            f1_score=0.92, auc_roc=0.96, sample_size=1000
        )
        assert result is not None
