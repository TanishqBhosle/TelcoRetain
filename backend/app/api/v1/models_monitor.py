"""Model monitoring API Router."""

import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends

from app.dependencies.auth import get_current_user, get_db, require_role
from app.repositories.model_repo import ModelRepository
from app.schemas.common import APIResponse
from app.schemas.models import MLModelResponse, ModelPerformanceLogResponse, ModelRetrainRequest
from app.services.model_service import ModelService

router = APIRouter(tags=["Models"])

ADMIN_ROLES = ["Super Admin", "Admin"]
MODEL_WRITE_ROLES = ["Super Admin", "Admin"]


async def get_model_service(db=Depends(get_db)) -> ModelService:
    return ModelService(ModelRepository(db))


@router.get("/models", response_model=APIResponse[List[MLModelResponse]])
async def list_models(
    service: ModelService = Depends(get_model_service),
    current_user=Depends(require_role(["Super Admin", "Admin", "Retention Manager", "Business Analyst"])),
):
    models = await service.list_models()
    return APIResponse(success=True, message="Models retrieved", data=[MLModelResponse.model_validate(item) for item in models])


@router.put("/models/{id}/retrain", response_model=APIResponse[None])
async def retrain_model(
    id: uuid.UUID,
    payload: ModelRetrainRequest,
    background_tasks: BackgroundTasks,
    service: ModelService = Depends(get_model_service),
    current_user=Depends(require_role(MODEL_WRITE_ROLES)),
):
    await service.get_model(id)
    await service.trigger_retraining(payload.dataset_version_id, background_tasks)
    return APIResponse(success=True, message="Model retraining queued", data=None)


@router.get("/models/{id}/activate", response_model=APIResponse[MLModelResponse])
async def activate_model(
    id: uuid.UUID,
    service: ModelService = Depends(get_model_service),
    current_user=Depends(require_role(MODEL_WRITE_ROLES)),
):
    model = await service.activate_model_version(id)
    return APIResponse(success=True, message="Model activated", data=MLModelResponse.model_validate(model))


@router.get("/models/{id}/performance-logs", response_model=APIResponse[List[ModelPerformanceLogResponse]])
async def model_performance(
    id: uuid.UUID,
    service: ModelService = Depends(get_model_service),
    current_user=Depends(require_role(["Super Admin", "Admin", "Business Analyst"])),
):
    logs = await service.get_performance_history(id)
    return APIResponse(
        success=True,
        message="Model performance history retrieved",
        data=[ModelPerformanceLogResponse.model_validate(item) for item in logs],
    )
