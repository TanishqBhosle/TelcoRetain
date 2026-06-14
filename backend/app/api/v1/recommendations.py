"""Recommendation API Router."""

import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_db
from app.repositories.customer_repo import CustomerRepository
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.recommendation_repo import RecommendationRepository
from app.schemas.common import APIResponse
from app.schemas.recommendations import OfferGenerateRequest, RecommendationResponse, RecommendationUpdate
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["Recommendations"])


async def get_recommendation_service(db=Depends(get_db)) -> RecommendationService:
    return RecommendationService(CustomerRepository(db), PredictionRepository(db), RecommendationRepository(db))


@router.post("/recommendations/generate", response_model=APIResponse[List[RecommendationResponse]])
async def generate_recommendations(
    payload: OfferGenerateRequest,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user=Depends(get_current_user),
):
    recommendations = await service.generate_recommendations(payload.customer_id)
    return APIResponse(
        success=True,
        message="Recommendations generated",
        data=[RecommendationResponse.model_validate(item) for item in recommendations],
    )


@router.get("/recommendations/{id}", response_model=APIResponse[RecommendationResponse])
async def recommendation_detail(
    id: uuid.UUID,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user=Depends(get_current_user),
):
    rec = await service.rec_repo.get_by_id(id)
    if rec is None:
        from app.exceptions.custom import NotFoundError

        raise NotFoundError(f"Recommendation with ID '{id}' not found")
    return APIResponse(success=True, message="Recommendation retrieved", data=RecommendationResponse.model_validate(rec))


@router.put("/recommendations/{id}", response_model=APIResponse[RecommendationResponse])
async def update_recommendation(
    id: uuid.UUID,
    payload: RecommendationUpdate,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user=Depends(get_current_user),
):
    rec = await service.update_recommendation_status(id, payload)
    return APIResponse(success=True, message="Recommendation updated", data=RecommendationResponse.model_validate(rec))
