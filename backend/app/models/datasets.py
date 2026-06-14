"""
Dataset Registry Models.
Tables:
  - datasets: Master dataset registry
  - dataset_versions: Dataset version tracking
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, String, Text, Numeric,
    UniqueConstraint, Index, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Dataset(Base, TimestampMixin, UUIDMixin):
    """
    Dataset registry for training and prediction data.
    Tracks dataset metadata and upload information.
    """
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    dataset_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # e.g., 'telco_churn', 'training', 'prediction'
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False  # Path to stored dataset file
    )
    format: Mapped[str] = mapped_column(
        String(20), nullable=False, default="csv"  # csv, parquet, json
    )
    row_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    column_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )
    tags: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True  # Key-value tags for categorization
    )

    # Relationships
    uploader: Mapped["User"] = relationship(
        "User", back_populates="uploaded_datasets"
    )
    versions: Mapped[List["DatasetVersion"]] = relationship(
        "DatasetVersion", back_populates="dataset", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Dataset id={self.id} name={self.name} type={self.dataset_type}>"


class DatasetVersion(Base, TimestampMixin, UUIDMixin):
    """
    Dataset version tracking.
    Maintains history of dataset iterations.
    """
    __tablename__ = "dataset_versions"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    change_description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    row_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    checksum: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True  # SHA256 hash for integrity verification
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="versions"
    )

    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_version"),
        Index("ix_dataset_versions_dataset", "dataset_id", "version_number"),
    )

    def __repr__(self) -> str:
        return f"<DatasetVersion dataset={self.dataset_id} v{self.version_number}>"