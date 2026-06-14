"""
Dataset Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.datasets import Dataset, DatasetVersion


class DatasetRepository:
    """Handles registry updates for datasets and dataset version history logs."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: uuid.UUID) -> Optional[Dataset]:
        """Fetch dataset details with versions loaded."""
        stmt = (
            select(Dataset)
            .where(Dataset.id == pk)
            .options(selectinload(Dataset.versions))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, dataset: Dataset) -> Dataset:
        """Register a new uploaded dataset."""
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def create_version(self, version: DatasetVersion) -> DatasetVersion:
        """Register a new version of a dataset."""
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version

    async def get_version_by_id(self, pk: uuid.UUID) -> Optional[DatasetVersion]:
        """Fetch a specific dataset version."""
        stmt = select(DatasetVersion).where(DatasetVersion.id == pk)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_datasets(self, dataset_type: Optional[str] = None) -> List[Dataset]:
        """List registered datasets, optionally filtered by type."""
        stmt = select(Dataset).options(selectinload(Dataset.versions))
        if dataset_type:
            stmt = stmt.where(Dataset.dataset_type == dataset_type)
        stmt = stmt.order_by(Dataset.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
