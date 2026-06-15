"""API router assembly."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.models_monitor import router as models_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.admin import router as admin_router
from app.api.v1.audit import router as audit_router
from app.api.v1.admin_roles import router as admin_roles_router
from app.api.v1.admin_security import router as admin_security_router
from app.api.v1.admin_system import router as admin_system_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(customers_router)
api_router.include_router(predictions_router)
api_router.include_router(recommendations_router)
api_router.include_router(campaigns_router)
api_router.include_router(dashboard_router)
api_router.include_router(models_router)
api_router.include_router(datasets_router)
api_router.include_router(admin_router)
api_router.include_router(audit_router)
api_router.include_router(admin_roles_router)
api_router.include_router(admin_security_router)
api_router.include_router(admin_system_router)
