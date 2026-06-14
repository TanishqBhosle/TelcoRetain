"""
ML Model Repository.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml import MLModel
from app.models.audit import ModelPerformanceLog


class ModelRepository:
    """Handles registry updates for ML models and validation monitoring metrics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: uuid.UUID) -> Optional[MLModel]:
        """Fetch model configuration by internal UUID."""
        stmt = select(MLModel).where(MLModel.id == pk)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_model(self) -> Optional[MLModel]:
        """Fetch the active ML model configuration."""
        stmt = select(MLModel).where(MLModel.is_active == True).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_model_by_version(self, name: str, version: str) -> Optional[MLModel]:
        """Fetch a specific model version by name."""
        stmt = select(MLModel).where(MLModel.name == name, MLModel.version == version)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, model: MLModel) -> MLModel:
        """Register a new trained model configuration."""
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def update(self, model: MLModel) -> MLModel:
        """Update model configuration state."""
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def activate_model(self, pk: uuid.UUID) -> Optional[MLModel]:
        """
        Marks model as active, and deactivates all other models.
        """
        # Deactivate all models
        stmt_deactivate = update(MLModel).values(is_active=False)
        await self.db.execute(stmt_deactivate)

        # Activate chosen model
        stmt_activate = update(MLModel).where(MLModel.id == pk).values(is_active=True)
        await self.db.execute(stmt_activate)
        await self.db.commit()

        return await self.get_by_id(pk)

    async def list_models(self, skip: int = 0, limit: int = 100) -> List[MLModel]:
        """Fetch all models in registry."""
        stmt = select(MLModel).order_by(MLModel.training_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save_performance_log(self, log: ModelPerformanceLog) -> ModelPerformanceLog:
        """Persist a new model performance evaluation metric."""
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_performance_logs(self, model_id: uuid.UUID) -> List[ModelPerformanceLog]:
        """Fetch historical performance validation checks for a model."""
        stmt = (
            select(ModelPerformanceLog)
            .where(ModelPerformanceLog.model_id == model_id)
            .order_by(ModelPerformanceLog.evaluation_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
