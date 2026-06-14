"""
Prediction Service.
"""

import datetime
from typing import List, Optional
import uuid

from fastapi import BackgroundTasks
from app.exceptions.custom import (
    CustomerNotFoundError, ModelNotLoadedError, PlatformException, NotFoundError
)
from app.models.ml import ChurnPrediction
from app.repositories.customer_repo import CustomerRepository
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.model_repo import ModelRepository
from app.repositories.usage_repo import UsageMetricsRepository
from app.repositories.network_repo import NetworkQualityRepository
from app.repositories.support_repo import SupportTicketRepository
from app.schemas.predictions import PredictionResponse, BulkPredictionResponse

# We will import ML modules. If not fully loaded, they might raise errors.
from ml.preprocessing.feature_pipeline import FeaturePipeline
from ml.inference.predictor import ChurnPredictor
from ml.inference.model_loader import ModelRegistry
from ml.explainability.shap_explainer import explain_and_save_async


class PredictionService:
    """Orchestrates predictions, coordinates data features assemblers, and triggers async SHAP explainers."""

    def __init__(
        self,
        customer_repo: CustomerRepository,
        prediction_repo: PredictionRepository,
        model_repo: ModelRepository,
        usage_repo: UsageMetricsRepository,
        network_repo: NetworkQualityRepository,
        support_repo: SupportTicketRepository,
    ) -> None:
        self.customer_repo = customer_repo
        self.prediction_repo = prediction_repo
        self.model_repo = model_repo
        self.usage_repo = usage_repo
        self.network_repo = network_repo
        self.support_repo = support_repo

    async def get_active_model_registry(self):
        """Fetch the active model config or raise."""
        active_model = await self.model_repo.get_active_model()
        if not active_model:
            raise ModelNotLoadedError("No active ML model version registered in system registry")
        # Validate that weights are loaded in registry
        if not ModelRegistry.is_loaded():
            raise ModelNotLoadedError("ML model registry weights are not loaded. Run retrain or check logs.")
        return active_model

    async def predict_single(
        self, customer_uuid: uuid.UUID, background_tasks: BackgroundTasks
    ) -> ChurnPrediction:
        """Run real-time churn prediction for a customer."""
        # 1. Check model registry
        active_model = await self.get_active_model_registry()

        # 2. Fetch customer behavior data
        customer = await self.customer_repo.get_by_id(customer_uuid)
        if not customer:
            raise CustomerNotFoundError(customer_uuid)

        latest_usage = await self.usage_repo.get_latest_metrics(customer_uuid)
        latest_network = await self.network_repo.get_latest(customer_uuid)
        complaint_count = await self.support_repo.get_complaint_count(customer_uuid)

        # 3. Assemble features using preprocessing pipeline
        features_df, raw_features_dict = FeaturePipeline.assemble_features(
            customer=customer,
            latest_usage=latest_usage,
            latest_network=latest_network,
            complaints_count=complaint_count
        )

        # 4. Run inference
        prob, confidence = ChurnPredictor.predict(features_df)
        risk_score = int(prob * 100)

        # Classify risk level
        if prob >= 0.70:
            risk_cat = "HIGH"
        elif prob >= 0.40:
            risk_cat = "MEDIUM"
        else:
            risk_cat = "LOW"

        # 5. Persist prediction
        prediction = ChurnPrediction(
            customer_id=customer_uuid,
            model_id=active_model.id,
            prediction_date=datetime.datetime.utcnow(),
            churn_probability=prob,
            risk_score=risk_score,
            risk_category=risk_cat,
            confidence_score=confidence,
            features_used=raw_features_dict,
        )
        saved_pred = await self.prediction_repo.save(prediction)

        # 6. Launch SHAP explainability asynchronously in background task
        background_tasks.add_task(
            explain_and_save_async,
            prediction_id=saved_pred.id,
            model_id=active_model.id,
            features_dict=raw_features_dict
        )

        return saved_pred

    async def predict_bulk(
        self, customer_uuids: List[uuid.UUID], background_tasks: BackgroundTasks
    ) -> BulkPredictionResponse:
        """Run churn predictions for a batch of customers."""
        predictions = []
        success_count = 0
        failure_count = 0

        for cust_uuid in customer_uuids:
            try:
                pred = await self.predict_single(cust_uuid, background_tasks)
                predictions.append(pred)
                success_count += 1
            except Exception:
                # Log bulk error for individual customer and proceed
                failure_count += 1

        # Map predictions to Response objects
        response_items = []
        for p in predictions:
            response_items.append(
                PredictionResponse(
                    id=p.id,
                    customer_id=p.customer_id,
                    model_id=p.model_id,
                    prediction_date=p.prediction_date,
                    churn_probability=float(p.churn_probability),
                    risk_score=p.risk_score,
                    risk_category=p.risk_category,
                    confidence_score=float(p.confidence_score) if p.confidence_score else None,
                    features_used=p.features_used,
                )
            )

        return BulkPredictionResponse(
            predictions=response_items,
            total_processed=len(customer_uuids),
            success_count=success_count,
            failure_count=failure_count,
        )

    async def list_predictions(self, page: int = 1, limit: int = 20) -> List[ChurnPrediction]:
        """Fetch list of churn predictions."""
        skip = (page - 1) * limit
        return await self.prediction_repo.list_predictions(skip, limit)

    async def get_prediction(self, prediction_uuid: uuid.UUID) -> ChurnPrediction:
        """Fetch detail of a single prediction."""
        pred = await self.prediction_repo.get_by_id(prediction_uuid)
        if not pred:
            raise NotFoundError(f"Prediction result '{prediction_uuid}' not found")
        return pred


def _run_batch_prediction(customer_ids: list):
    """Synchronous entry point for APScheduler batch prediction jobs."""
    import asyncio
    import logging
    from app.core.database import AsyncSessionLocal
    from app.repositories.customer_repo import CustomerRepository
    from app.repositories.prediction_repo import PredictionRepository
    from app.repositories.model_repo import ModelRepository
    from app.repositories.usage_repo import UsageMetricsRepository
    from app.repositories.network_repo import NetworkQualityRepository
    from app.repositories.support_repo import SupportTicketRepository

    logger = logging.getLogger(__name__)
    logger.info(f"Starting batch prediction for {len(customer_ids)} customers")

    async def _run():
        async with AsyncSessionLocal() as db:
            service = PredictionService(
                CustomerRepository(db),
                PredictionRepository(db),
                ModelRepository(db),
                UsageMetricsRepository(db),
                NetworkQualityRepository(db),
                SupportTicketRepository(db),
            )
            success = 0
            failed = 0
            for cid in customer_ids:
                try:
                    import uuid as _uuid
                    await service.predict_single(_uuid.UUID(cid), BackgroundTasks())
                    success += 1
                except Exception as e:
                    logger.error(f"Batch prediction failed for {cid}: {e}")
                    failed += 1
            logger.info(f"Batch prediction complete: {success} success, {failed} failed")

    asyncio.run(_run())
