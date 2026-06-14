"""
Admin & Systems Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SystemHealthResponse(BaseModel):
    """Aggregate system and service health status."""

    status: str = Field(..., description="Overall system health status (healthy, degraded, unhealthy)")
    database_connected: bool = Field(..., description="Database connectivity status")
    redis_connected: bool = Field(..., description="Redis connectivity status")
    ml_models_loaded: bool = Field(..., description="ML model initialization status")
    uptime_seconds: float = Field(..., description="Seconds since server startup")
    system_metrics: Dict[str, Any] = Field(..., description="Details regarding OS memory and cpu usage")


class AuditLogResponse(BaseModel):
    """Platform action audit trace."""

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    request_payload: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApiLogResponse(BaseModel):
    """Detailed API traffic log."""

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    endpoint: str
    method: str
    request_headers: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: int
    response_time_ms: Optional[int] = None
    ip_address: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
