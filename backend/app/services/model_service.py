"""
Model Registry & Monitoring Service.
"""

import sys
import subprocess
import uuid
from typing import List, Optional

from fastapi import BackgroundTasks
from app.exceptions.custom import NotFoundError, PlatformException
from app.models.ml import MLModel
from app.models.audit import ModelPerformanceLog
from app.repositories.model_repo import ModelRepository
import structlog

logger = structlog.get_logger(__name__)


class ModelService:
    """Manages active ML models, evaluation metrics, and retraining triggers."""

    def __init__(self, model_repo: ModelRepository) -> None:
        self.model_repo = model_repo

    async def get_model(self, model_uuid: uuid.UUID) -> MLModel:
        """Fetch model configuration details."""
        model = await self.model_repo.get_by_id(model_uuid)
        if not model:
            raise NotFoundError(f"Model version '{model_uuid}' not found")
        return model

    async def list_models(self, skip: int = 0, limit: int = 100) -> List[MLModel]:
        """Fetch all models in registry."""
        return await self.model_repo.list_models(skip, limit)

    async def activate_model_version(self, model_uuid: uuid.UUID) -> MLModel:
        """Marks model version active and disables others."""
        model = await self.get_model(model_uuid)
        return await self.model_repo.activate_model(model_uuid)

    async def add_performance_metrics(
        self,
        model_uuid: uuid.UUID,
        accuracy: float,
        precision: float,
        recall: float,
        f1_score: float,
        auc_roc: float,
        sample_size: int,
        drift_detected: bool = False,
        notes: Optional[str] = None,
    ) -> ModelPerformanceLog:
        """Append model validation run metrics."""
        await self.get_model(model_uuid)

        log = ModelPerformanceLog(
            model_id=model_uuid,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            auc_roc=auc_roc,
            sample_size=sample_size,
            drift_detected=drift_detected,
            notes=notes,
        )
        return await self.model_repo.save_performance_log(log)

    async def get_performance_history(self, model_uuid: uuid.UUID) -> List[ModelPerformanceLog]:
        """Fetch evaluation run metrics for a model."""
        await self.get_model(model_uuid)
        return await self.model_repo.get_performance_logs(model_uuid)

    async def trigger_retraining(self, dataset_version_id: Optional[uuid.UUID], background_tasks: BackgroundTasks) -> None:
        """Triggers the model training script in the background."""
        # Enqueue background task to run training script
        background_tasks.add_task(self._run_retraining_process, dataset_version_id)

    def _run_retraining_process(self, dataset_version_id: Optional[uuid.UUID]) -> None:
        """Invokes scripts/train_models.py via subprocess."""
        logger.info("triggering_model_retraining", dataset_version=str(dataset_version_id))
        try:
            cmd = [sys.executable, "scripts/train_models.py"]
            if dataset_version_id:
                cmd.extend(["--dataset-version-id", str(dataset_version_id)])

            # Run training subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("model_retraining_success", output=result.stdout)
            else:
                logger.error("model_retraining_failed", error=result.stderr, output=result.stdout)
        except Exception as e:
            logger.error("model_retraining_exception", error=str(e))


def _run_retraining(dataset_version_id: str | None = None):
    """Synchronous entry point for APScheduler retraining jobs."""
    import asyncio
    import logging
    from app.core.database import AsyncSessionLocal
    from app.repositories.model_repo import ModelRepository

    _logger = logging.getLogger(__name__)
    _logger.info(f"Starting model retraining, dataset_version_id={dataset_version_id}")

    async def _run():
        async with AsyncSessionLocal() as db:
            service = ModelService(ModelRepository(db))
            sv_id = uuid.UUID(dataset_version_id) if dataset_version_id else None
            service._run_retraining_process(sv_id)

    asyncio.run(_run())
