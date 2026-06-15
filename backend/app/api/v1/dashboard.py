"""Dashboard and analytics API Router."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_db, require_role
from app.repositories.campaign_repo import CampaignRepository
from app.schemas.common import APIResponse
from app.schemas.dashboard import (
    DashboardChurnTrendsResponse,
    DashboardKPIResponse,
    DashboardOperatorResponse,
    DashboardRegionalResponse,
    DashboardRevenueRiskResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Dashboard"])

DASHBOARD_READ_ROLES = ["Super Admin", "Admin", "Retention Manager", "Marketing Manager", "Business Analyst", "Executive Viewer"]


async def get_analytics_service(db=Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db, CampaignRepository(db))


@router.get("/dashboard/kpis", response_model=APIResponse[DashboardKPIResponse])
async def dashboard_kpis(
    service: AnalyticsService = Depends(get_analytics_service),
    current_user=Depends(require_role(DASHBOARD_READ_ROLES)),
):
    return APIResponse(success=True, message="Dashboard KPIs retrieved", data=await service.get_dashboard_kpis())


@router.get("/dashboard/churn-trends", response_model=APIResponse[DashboardChurnTrendsResponse])
async def churn_trends(
    service: AnalyticsService = Depends(get_analytics_service),
    current_user=Depends(require_role(DASHBOARD_READ_ROLES)),
):
    return APIResponse(success=True, message="Churn trends retrieved", data=await service.get_churn_trends())


@router.get("/dashboard/revenue-risk", response_model=APIResponse[DashboardRevenueRiskResponse])
async def revenue_risk(
    service: AnalyticsService = Depends(get_analytics_service),
    current_user=Depends(require_role(DASHBOARD_READ_ROLES)),
):
    return APIResponse(success=True, message="Revenue risk retrieved", data=await service.get_revenue_risk_customers())


@router.get("/dashboard/regional-analysis", response_model=APIResponse[DashboardRegionalResponse])
async def regional_analysis(
    service: AnalyticsService = Depends(get_analytics_service),
    current_user=Depends(require_role(DASHBOARD_READ_ROLES)),
):
    return APIResponse(success=True, message="Regional analysis retrieved", data=await service.get_regional_analysis())


@router.get("/dashboard/operator-analysis", response_model=APIResponse[DashboardOperatorResponse])
async def operator_analysis(
    service: AnalyticsService = Depends(get_analytics_service),
    current_user=Depends(require_role(DASHBOARD_READ_ROLES)),
):
    return APIResponse(success=True, message="Operator analysis retrieved", data=await service.get_operator_analysis())
