"""Seed bootstrap roles, permissions, admin user, and sample model registry."""

from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.ml import MLModel
from app.models.users import Permission, Role, RolePermission, User
from sqlalchemy import select


ROLE_PERMISSIONS = {
    "Super Admin": [
        "admin:full_access",
        "users:create", "users:read", "users:update", "users:delete",
        "roles:manage",
        "models:read", "models:write", "models:retrain", "models:activate",
        "datasets:read", "datasets:write",
        "audit:read",
        "system:settings", "system:health",
        "customers:read",
        "predictions:read", "predictions:write",
        "campaigns:read", "campaigns:write",
        "recommendations:read", "recommendations:write",
        "analytics:read",
        "reports:read", "reports:export",
    ],
    "Admin": [
        "users:create", "users:read", "users:update", "users:delete",
        "roles:read",
        "models:read", "models:write", "models:retrain", "models:activate",
        "datasets:read", "datasets:write",
        "audit:read",
        "system:health",
        "customers:read",
    ],
    "Retention Manager": [
        "customers:read",
        "predictions:read", "predictions:write",
        "recommendations:read", "recommendations:write",
        "campaigns:read", "campaigns:write",
        "analytics:read",
        "dashboard:read",
    ],
    "Marketing Manager": [
        "campaigns:read", "campaigns:write",
        "recommendations:read",
        "analytics:read",
        "dashboard:read",
    ],
    "Business Analyst": [
        "analytics:read",
        "reports:read", "reports:export",
        "customers:read",
        "dashboard:read",
    ],
    "Customer Support Executive": [
        "customers:read",
        "predictions:read",
        "recommendations:read",
    ],
    "Executive Viewer": [
        "dashboard:read",
        "reports:read",
        "analytics:read",
    ],
}


async def get_or_create(session, model, defaults=None, **filters):
    result = await session.execute(select(model).filter_by(**filters))
    instance = result.scalar_one_or_none()
    if instance is not None:
        return instance
    instance = model(**filters, **(defaults or {}))
    session.add(instance)
    await session.flush()
    return instance


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        permissions = {}
        for names in ROLE_PERMISSIONS.values():
            for permission_name in names:
                permissions[permission_name] = await get_or_create(
                    session,
                    Permission,
                    permission_name=permission_name,
                    defaults={"description": permission_name.replace(":", " ").title()},
                )

        roles = {}
        for role_name, permission_names in ROLE_PERMISSIONS.items():
            roles[role_name] = await get_or_create(
                session,
                Role,
                name=role_name,
                defaults={"description": f"{role_name} platform role"},
            )
            for permission_name in permission_names:
                await get_or_create(
                    session,
                    RolePermission,
                    role_id=roles[role_name].id,
                    permission_id=permissions[permission_name].id,
                )

        await get_or_create(
            session,
            User,
            email=settings.FIRST_ADMIN_EMAIL,
            defaults={
                "role_id": roles["Super Admin"].id,
                "full_name": settings.FIRST_ADMIN_NAME,
                "password_hash": get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                "is_active": True,
                "email_verified": True,
            },
        )

        metadata_path = Path(settings.ML_MODELS_PATH) / "metadata.json"
        if metadata_path.exists():
            import json

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            for model_name in metadata.get("selected_models", []):
                await get_or_create(
                    session,
                    MLModel,
                    name=model_name,
                    version=settings.ML_MODEL_VERSION,
                    defaults={
                        "model_type": model_name,
                        "model_path": str(Path(settings.ML_MODELS_PATH) / f"{model_name}.pkl"),
                        "feature_columns": metadata.get("feature_columns", []),
                        "accuracy": metadata.get("metrics", {}).get(model_name, {}).get("accuracy"),
                        "auc_score": metadata.get("metrics", {}).get(model_name, {}).get("auc_score"),
                        "is_active": model_name == metadata.get("selected_models", [None])[0],
                        "description": "Seeded from local training artifacts",
                    },
                )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
