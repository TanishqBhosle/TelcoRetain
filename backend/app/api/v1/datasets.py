"""Dataset API Router."""

import hashlib
import os
import uuid
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.core.config import settings
from app.dependencies.auth import get_current_user, get_db, require_role
from app.exceptions.custom import ValidationError
from app.repositories.dataset_repo import DatasetRepository
from app.schemas.common import APIResponse
from app.schemas.datasets import DatasetCreateRequest, DatasetResponse, DatasetVersionResponse
from app.services.dataset_service import DatasetService

router = APIRouter(tags=["Datasets"])

ADMIN_ROLES = ["Super Admin", "Admin"]

UPLOAD_DIR = Path(settings.ML_ARTIFACTS_PATH).parent / "uploads"
ALLOWED_EXTENSIONS = {".csv", ".parquet", ".xlsx"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


async def get_dataset_service(db=Depends(get_db)) -> DatasetService:
    return DatasetService(DatasetRepository(db))


@router.post("/datasets/upload", response_model=APIResponse[DatasetResponse])
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    dataset_type: str = Form("training"),
    tags: str = Form(""),
    service: DatasetService = Depends(get_dataset_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    """Upload a dataset file (CSV, Parquet, or Excel)."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise ValidationError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)}MB")

    checksum = hashlib.sha256(contents).hexdigest()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(contents)

    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext == ".parquet":
            df = pd.read_parquet(file_path)
        elif ext == ".xlsx":
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame()
        row_count = len(df)
        column_count = len(df.columns)
    except Exception:
        row_count = 0
        column_count = 0

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    payload = DatasetCreateRequest(
        name=name,
        description=description,
        dataset_type=dataset_type,
        file_path=str(file_path),
        format=ext.lstrip("."),
        row_count=row_count,
        column_count=column_count,
        tags=tag_list,
    )
    dataset = await service.register_dataset(current_user.id, payload)
    return APIResponse(success=True, message="Dataset uploaded and registered", data=DatasetResponse.model_validate(dataset))


@router.get("/datasets", response_model=APIResponse[List[DatasetResponse]])
async def list_datasets(
    dataset_type: Optional[str] = Query(None),
    service: DatasetService = Depends(get_dataset_service),
    current_user=Depends(require_role(["Super Admin", "Admin", "Retention Manager", "Business Analyst"])),
):
    datasets = await service.list_datasets(dataset_type=dataset_type)
    return APIResponse(success=True, message="Datasets retrieved", data=[DatasetResponse.model_validate(item) for item in datasets])


@router.get("/datasets/{id}/versions", response_model=APIResponse[List[DatasetVersionResponse]])
async def dataset_versions(
    id: uuid.UUID,
    service: DatasetService = Depends(get_dataset_service),
    current_user=Depends(require_role(["Super Admin", "Admin"])),
):
    dataset = await service.get_dataset(id)
    return APIResponse(
        success=True,
        message="Dataset versions retrieved",
        data=[DatasetVersionResponse.model_validate(item) for item in dataset.versions],
    )


@router.post("/datasets/{id}/versions", response_model=APIResponse[DatasetVersionResponse])
async def create_dataset_version(
    id: uuid.UUID,
    file: UploadFile = File(...),
    change_description: str = Form(""),
    service: DatasetService = Depends(get_dataset_service),
    current_user=Depends(require_role(ADMIN_ROLES)),
):
    """Upload a new version of an existing dataset."""
    dataset = await service.get_dataset(id)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' not allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise ValidationError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)}MB")

    checksum = hashlib.sha256(contents).hexdigest()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(contents)

    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext == ".parquet":
            df = pd.read_parquet(file_path)
        elif ext == ".xlsx":
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame()
        row_count = len(df)
    except Exception:
        row_count = 0

    version = await service.create_dataset_version(
        dataset_id=id,
        file_path=str(file_path),
        row_count=row_count,
        checksum=checksum,
        change_description=change_description,
        created_by=current_user.id,
    )
    return APIResponse(success=True, message="Dataset version created", data=DatasetVersionResponse.model_validate(version))
