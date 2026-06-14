"""
User & Access Management Models:
  - roles
  - permissions
  - users
  - role_permissions (join table)
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint, func,
)
from app.models.types import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Role(Base):
    """RBAC Roles: Admin, Analyst, Retention Manager, Marketing Manager, etc."""
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name}>"


class Permission(Base):
    """Granular permission registry."""
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    permission_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission"
    )

    def __repr__(self) -> str:
        return f"<Permission id={self.id} name={self.permission_name}>"


class RolePermission(Base):
    """Many-to-many join table between roles and permissions."""
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_permissions"
    )


class User(Base):
    """
    Platform users with RBAC role assignment.
    Includes security fields for lockout and email verification.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Added security fields (Gap G5, G13) ---
    email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    verification_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    audit_logs: Mapped[List["AuditLog"]] = relationship(  # type: ignore[name-defined]
        "AuditLog", back_populates="user"
    )
    api_logs: Mapped[List["ApiLog"]] = relationship(  # type: ignore[name-defined]
        "ApiLog", back_populates="user"
    )
    uploaded_datasets: Mapped[List["Dataset"]] = relationship(  # type: ignore[name-defined]
        "Dataset", back_populates="uploader"
    )
    created_campaigns: Mapped[List["Campaign"]] = relationship(  # type: ignore[name-defined]
        "Campaign", back_populates="creator"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role_id}>"

    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        from datetime import timezone
        return datetime.now(timezone.utc) < self.locked_until.replace(tzinfo=timezone.utc)
