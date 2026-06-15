"""Prediction API Router."""

import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Query

from app.dependencies.auth import get_current_user, get_db, require_role
from app.repositories.customer_repo import CustomerRepository
from app.repositories.model_repo import ModelRepository
from app.repositories.network_repo import NetworkQualityRepository
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.support_repo import SupportTicketRepository
from app.repositories.usage_repo import UsageMetricsRepository
from app.schemas.common import APIResponse
from app.schemas.explanations import ChurnExplanationResponse
from app.schemas.predictions import BulkPredictRequest, BulkPredictionResponse, PredictRequest, PredictionResponse
from app.services.explanation_service import ExplanationService
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["Predictions"])

PREDICTION_WRITE_ROLES = ["Super Admin", "Admin", "Retention Manager"]
PREDICTION_READ_ROLES = ["Super Admin", "Admin", "Retention Manager", "Business Analyst", "Customer Support Executive"]


async def get_prediction_service(db=Depends(get_db)) -> PredictionService:
    return PredictionService(
        CustomerRepository(db),
        PredictionRepository(db),
        ModelRepository(db),
        UsageMetricsRepository(db),
        NetworkQualityRepository(db),
        SupportTicketRepository(db),
    )


async def get_explanation_service(db=Depends(get_db)) -> ExplanationService:
    return ExplanationService(PredictionRepository(db))


@router.post("/predictions/predict", response_model=APIResponse[PredictionResponse])
async def predict(
    payload: PredictRequest,
    background_tasks: BackgroundTasks,
    service: PredictionService = Depends(get_prediction_service),
    current_user=Depends(require_role(PREDICTION_WRITE_ROLES)),
):
    prediction = await service.predict_single(payload.customer_id, background_tasks)
    return APIResponse(success=True, message="Prediction completed", data=PredictionResponse.model_validate(prediction))


@router.post("/predictions/bulk", response_model=APIResponse[BulkPredictionResponse])
async def predict_bulk(
    payload: BulkPredictRequest,
    background_tasks: BackgroundTasks,
    service: PredictionService = Depends(get_prediction_service),
    current_user=Depends(require_role(PREDICTION_WRITE_ROLES)),
):
    result = await service.predict_bulk(payload.customer_ids, background_tasks)
    return APIResponse(success=True, message="Bulk prediction completed", data=result)


@router.get("/predictions/history", response_model=APIResponse[List[PredictionResponse]])
async def prediction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: PredictionService = Depends(get_prediction_service),
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
):
    predictions = await service.list_predictions(page=page, limit=limit)
    return APIResponse(
        success=True,
        message="Prediction history retrieved",
        data=[PredictionResponse.model_validate(item) for item in predictions],
    )


@router.get("/predictions/{id}", response_model=APIResponse[PredictionResponse])
async def prediction_detail(
    id: uuid.UUID,
    service: PredictionService = Depends(get_prediction_service),
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
):
    prediction = await service.get_prediction(id)
    return APIResponse(success=True, message="Prediction retrieved", data=PredictionResponse.model_validate(prediction))


@router.get("/predictions/{id}/explanation", response_model=APIResponse[ChurnExplanationResponse])
async def prediction_explanation(
    id: uuid.UUID,
    service: ExplanationService = Depends(get_explanation_service),
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
):
    explanation = await service.get_prediction_explanation(id)
    return APIResponse(success=True, message="Prediction explanation retrieved", data=explanation)


@router.get("/predictions/{id}/reasons", response_model=APIResponse[List[str]])
async def prediction_reasons(
    id: uuid.UUID,
    service: ExplanationService = Depends(get_explanation_service),
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
):
    explanation = await service.get_prediction_explanation(id)
    return APIResponse(success=True, message="Churn reasons retrieved", data=explanation.reasons)
