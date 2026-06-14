"""Tests for dataset service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import NotFoundError


@pytest.mark.asyncio
class TestDatasetService:
    """Tests for DatasetService methods."""

    @patch("app.services.dataset_service.DatasetRepository")
    async def test_get_dataset_success(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_dataset = MagicMock()
        mock_dataset.id = uuid.uuid4()
        mock_dataset.name = "Test Dataset"
        mock_dataset.versions = []
        mock_repo.get_by_id.return_value = mock_dataset

        from app.services.dataset_service import DatasetService
        service = DatasetService(mock_repo)

        result = await service.get_dataset(mock_dataset.id)
        assert result.name == "Test Dataset"

    @patch("app.services.dataset_service.DatasetRepository")
    async def test_get_dataset_not_found(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        from app.services.dataset_service import DatasetService
        service = DatasetService(mock_repo)

        with pytest.raises(NotFoundError):
            await service.get_dataset(uuid.uuid4())

    @patch("app.services.dataset_service.DatasetRepository")
    async def test_list_datasets(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.list_datasets.return_value = [MagicMock(), MagicMock()]

        from app.services.dataset_service import DatasetService
        service = DatasetService(mock_repo)

        result = await service.list_datasets()
        assert len(result) == 2

    @patch("app.services.dataset_service.DatasetRepository")
    async def test_register_dataset(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_dataset = MagicMock()
        mock_dataset.id = uuid.uuid4()
        mock_repo.create.return_value = mock_dataset

        from app.services.dataset_service import DatasetService
        from app.schemas.datasets import DatasetCreateRequest
        service = DatasetService(mock_repo)

        payload = DatasetCreateRequest(
            name="Training Data",
            description="Customer churn data",
            dataset_type="training",
            file_path="/data/train.csv",
            format="csv",
            row_count=1000,
            column_count=15,
        )

        result = await service.register_dataset(uuid.uuid4(), payload)
        assert result is not None
