"""
Common API schemas.
"""

from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard envelope for all API responses."""

    success: bool = Field(..., description="Flag indicating if the request was successful")
    message: str = Field(..., description="Readable status or feedback message")
    data: Optional[T] = Field(None, description="The response payload")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of response generation",
    )
    path: Optional[str] = Field(None, description="The endpoint path accessed")


class PaginatedData(BaseModel, Generic[T]):
    """Wrapper for paginated response collections."""

    items: list[T] = Field(..., description="List of items for the current page")
    total: int = Field(..., description="Total count of items matching the query")
    page: int = Field(..., description="Current page index")
    limit: int = Field(..., description="Page size limit")
    pages: int = Field(..., description="Total number of pages")
