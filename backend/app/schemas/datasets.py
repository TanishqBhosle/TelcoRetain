"""
Dataset Pydantic schemas.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DatasetCreateRequest(BaseModel):
    """Payload to register a new dataset entry."""

    name: str = Field(..., min_length=2, max_length=200, description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    dataset_type: str = Field(..., description="Dataset purpose: e.g. training, prediction")
    file_path: str = Field(..., description="Path to stored file")
    format: str = Field("csv", description="Format: csv, parquet, json")
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    tags: Optional[Dict[str, str]] = None


class DatasetVersionResponse(BaseModel):
    """Details of a specific dataset version."""

    id: uuid.UUID
    dataset_id: uuid.UUID
    version_number: int
    change_description: Optional[str] = None
    file_path: str
    row_count: Optional[int] = None
    checksum: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetResponse(BaseModel):
    """Details of a registered dataset."""

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    dataset_type: str
    file_path: str
    format: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    uploaded_by: uuid.UUID
    is_active: bool
    tags: Optional[Dict[str, Any]] = None
    created_at: datetime
    versions: List[DatasetVersionResponse] = []

    class Config:
        from_attributes = True
