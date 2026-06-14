"""
Dataset Service.
"""

import uuid
from typing import List, Optional
import pandas as pd

from app.exceptions.custom import NotFoundError
from app.models.datasets import Dataset, DatasetVersion
from app.repositories.dataset_repo import DatasetRepository
from app.schemas.datasets import DatasetCreateRequest


class DatasetService:
    """Manages datasets and file versioning for model training and predictions."""

    def __init__(self, dataset_repo: DatasetRepository) -> None:
        self.dataset_repo = dataset_repo

    async def register_dataset(self, uploader_uuid: uuid.UUID, req: DatasetCreateRequest) -> Dataset:
        """Register a new uploaded dataset, analyzing rows and columns."""
        # Calculate row and column counts from file path if possible
        row_count = req.row_count
        col_count = req.column_count
        if req.file_path.endswith(".csv"):
            try:
                # Read header to determine row and column count
                df = pd.read_csv(req.file_path)
                row_count = len(df)
                col_count = len(df.columns)
            except Exception:
                pass

        dataset = Dataset(
            name=req.name,
            description=req.description,
            dataset_type=req.dataset_type,
            file_path=req.file_path,
            format=req.format,
            row_count=row_count,
            column_count=col_count,
            uploaded_by=uploader_uuid,
            is_active=True,
            tags=req.tags,
        )

        return await self.dataset_repo.create(dataset)

    async def get_dataset(self, dataset_uuid: uuid.UUID) -> Dataset:
        """Fetch dataset profile."""
        dataset = await self.dataset_repo.get_by_id(dataset_uuid)
        if not dataset:
            raise NotFoundError(f"Dataset '{dataset_uuid}' not found")
        return dataset

    async def list_datasets(self, dataset_type: Optional[str] = None) -> List[Dataset]:
        """List registered datasets."""
        return await self.dataset_repo.list_datasets(dataset_type)

    async def create_dataset_version(
        self,
        dataset_id: uuid.UUID,
        file_path: str,
        row_count: Optional[int] = None,
        checksum: Optional[str] = None,
        change_description: str = "",
        created_by: Optional[uuid.UUID] = None,
    ) -> DatasetVersion:
        """Create a new version for an existing dataset."""
        dataset = await self.get_dataset(dataset_id)

        # Get next version number
        next_ver = len(dataset.versions) + 1

        if row_count is None and file_path.endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
                row_count = len(df)
            except Exception:
                pass

        version = DatasetVersion(
            dataset_id=dataset_id,
            version_number=next_ver,
            change_description=change_description,
            file_path=file_path,
            row_count=row_count,
            checksum=checksum,
            created_by=created_by,
        )

        return await self.dataset_repo.create_version(version)
