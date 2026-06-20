"""Prediction API Router."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies.auth import get_current_user, get_db, require_role
from app.schemas.common import APIResponse
from app.schemas.predictions import (
    BulkPredictRequest,
    BulkPredictionResponse,
    LegacyPredictRequest,
    LegacyPredictionResponse,
    PredictRequest,
    PredictionResponse,
)
from app.services.prediction_service import PredictionService
from ml.inference.artifact_loader import ArtifactRegistry

router = APIRouter(tags=["Predictions"])

PREDICTION_WRITE_ROLES = ["Super Admin", "Admin", "Retention Manager"]
PREDICTION_READ_ROLES = ["Super Admin", "Admin", "Retention Manager", "Business Analyst", "Customer Support Executive"]


@router.post("/predictions/predict", response_model=APIResponse[PredictionResponse])
async def predict(
    payload: PredictRequest,
    current_user=Depends(require_role(PREDICTION_WRITE_ROLES)),
):
    """Run churn prediction using the refactored ML pipeline.

    Accepts IBM Telco customer fields and returns churn probability,
    risk category, SHAP-based churn drivers, and retention recommendations.

    Returns HTTP 503 if model artifacts are not loaded.
    """
    # Task 9.4: Return 503 if artifacts not loaded
    if not ArtifactRegistry.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="ML model artifacts not loaded. Service temporarily unavailable.",
        )

    # Convert Pydantic model to raw dict for the pipeline
    raw_input = payload.model_dump(exclude_none=True)
    # Remove customer_id from feature input (it's metadata, not a feature)
    raw_input.pop("customer_id", None)

    result = PredictionService.predict(raw_input)
    return APIResponse(success=True, message="Prediction completed", data=result)


# --- Legacy endpoints for backward compatibility (bulk, history, detail, explanations) ---


@router.post("/predictions/bulk", response_model=APIResponse[BulkPredictionResponse])
async def predict_bulk(
    payload: BulkPredictRequest,
    current_user=Depends(require_role(PREDICTION_WRITE_ROLES)),
):
    """Bulk prediction endpoint (legacy - requires DB-backed service)."""
    # This endpoint requires the legacy DB-backed service which is not part
    # of the new pipeline. Return 503 until migrated.
    raise HTTPException(
        status_code=503,
        detail="Bulk prediction endpoint is being migrated. Use /predictions/predict for single predictions.",
    )


@router.get("/predictions/history", response_model=APIResponse[List[LegacyPredictionResponse]])
async def prediction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
    db=Depends(get_db),
):
    """Fetch prediction history from the database."""
    from app.repositories.prediction_repo import PredictionRepository

    prediction_repo = PredictionRepository(db)
    skip = (page - 1) * limit
    predictions = await prediction_repo.list_predictions(skip, limit)
    return APIResponse(
        success=True,
        message="Prediction history retrieved",
        data=[LegacyPredictionResponse.model_validate(item) for item in predictions],
    )


@router.get("/predictions/{id}", response_model=APIResponse[LegacyPredictionResponse])
async def prediction_detail(
    id: uuid.UUID,
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
    db=Depends(get_db),
):
    """Fetch a single prediction by ID from the database."""
    from app.repositories.prediction_repo import PredictionRepository
    from app.exceptions.custom import NotFoundError

    prediction_repo = PredictionRepository(db)
    pred = await prediction_repo.get_by_id(id)
    if not pred:
        raise HTTPException(status_code=404, detail=f"Prediction '{id}' not found")
    return APIResponse(
        success=True,
        message="Prediction retrieved",
        data=LegacyPredictionResponse.model_validate(pred),
    )


@router.get("/predictions/{id}/explanation")
async def prediction_explanation(
    id: uuid.UUID,
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
    db=Depends(get_db),
):
    """Fetch SHAP explanation for a prediction."""
    from app.repositories.prediction_repo import PredictionRepository
    from app.schemas.explanations import ChurnExplanationResponse
    from app.services.explanation_service import ExplanationService

    prediction_repo = PredictionRepository(db)
    service = ExplanationService(prediction_repo)
    explanation = await service.get_prediction_explanation(id)
    return APIResponse(success=True, message="Prediction explanation retrieved", data=explanation)


@router.get("/predictions/{id}/reasons", response_model=APIResponse[List[str]])
async def prediction_reasons(
    id: uuid.UUID,
    current_user=Depends(require_role(PREDICTION_READ_ROLES)),
    db=Depends(get_db),
):
    """Fetch churn reasons for a prediction."""
    from app.repositories.prediction_repo import PredictionRepository
    from app.services.explanation_service import ExplanationService

    prediction_repo = PredictionRepository(db)
    service = ExplanationService(prediction_repo)
    explanation = await service.get_prediction_explanation(id)
    return APIResponse(success=True, message="Churn reasons retrieved", data=explanation.reasons)
