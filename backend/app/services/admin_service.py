"""
Admin & Systems Health Service.
"""

import time
import uuid
from typing import Optional, List, Tuple

from app.core.database import check_database_connection
from app.core.security import get_redis
from app.models.audit import AuditLog, ApiLog
from app.repositories.audit_repo import AuditRepository
from app.schemas.admin import SystemHealthResponse, AuditLogResponse, ApiLogResponse
from ml.inference.artifact_loader import ArtifactRegistry as ModelRegistry

# Capture start time for uptime calculation
START_TIME = time.time()


class AdminService:
    """Manages platform security log lookups and system resource status checks."""

    def __init__(self, audit_repo: AuditRepository) -> None:
        self.audit_repo = audit_repo

    async def get_system_health(self) -> SystemHealthResponse:
        """Query DB connections, Redis connection status, ML models registry state, and uptime."""
        # 1. DB connection check
        db_connected = await check_database_connection()

        # 2. Redis connection check
        redis_connected = False
        try:
            redis_client = await get_redis()
            if redis_client:
                redis_connected = True
        except Exception:
            pass

        # 3. ML Models check
        ml_loaded = False
        try:
            ml_loaded = ModelRegistry.is_loaded()
        except Exception:
            pass

        # 4. Overall status
        if db_connected and redis_connected and ml_loaded:
            overall_status = "healthy"
        elif db_connected:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        # 5. Uptime
        uptime = time.time() - START_TIME

        # 6. Gather CPU/RAM metrics safely when psutil is installed.
        cpu_percent = None
        memory_percent = None
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
        except ImportError:
            pass

        return SystemHealthResponse(
            status=overall_status,
            database_connected=db_connected,
            redis_connected=redis_connected,
            ml_models_loaded=ml_loaded,
            uptime_seconds=uptime,
            system_metrics={
                "cpu_utilization_percent": cpu_percent,
                "memory_utilization_percent": memory_percent,
            }
        )

    async def list_audit_logs(
        self,
        user_uuid: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[AuditLogResponse], int]:
        """Fetch audit logs (paginated)."""
        skip = (page - 1) * limit
        items, total = await self.audit_repo.list_audit_logs(
            user_id=user_uuid,
            action=action,
            resource_type=resource_type,
            skip=skip,
            limit=limit,
        )

        response_items = [
            AuditLogResponse(
                id=item.id,
                user_id=item.user_id,
                action=item.action,
                resource_type=item.resource_type,
                resource_id=item.resource_id,
                request_payload=item.request_payload,
                response_status=item.response_status,
                ip_address=item.ip_address,
                user_agent=item.user_agent,
                additional_data=item.additional_data,
                created_at=item.created_at,
            )
            for item in items
        ]

        return response_items, total

    async def list_api_logs(self, page: int = 1, limit: int = 100) -> List[ApiLogResponse]:
        """Fetch API transaction logs (paginated)."""
        skip = (page - 1) * limit
        items = await self.audit_repo.list_api_logs(skip, limit)

        return [
            ApiLogResponse(
                id=item.id,
                user_id=item.user_id,
                endpoint=item.endpoint,
                method=item.method,
                request_headers=item.request_headers,
                request_body=item.request_body,
                response_status=item.response_status,
                response_time_ms=item.response_time_ms,
                ip_address=item.ip_address,
                error_message=item.error_message,
                created_at=item.created_at,
            )
            for item in items
        ]
