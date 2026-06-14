"""Create all tables and seed data for SQLite development."""
import sys
sys.path.insert(0, ".")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings

# Use synchronous SQLite engine for init
sync_url = settings.DATABASE_URL.replace("+aiosqlite", "")
engine_sync = create_engine(sync_url, connect_args={"check_same_thread": False})

from app.models.base import Base
from app.models import *  # noqa

def init_db():
    Base.metadata.create_all(bind=engine_sync)
    print("Database tables created.")

def seed():
    from app.core.security import get_password_hash
    from app.models.users import User, Role, Permission, RolePermission
    from app.models.ml import MLModel
    from sqlalchemy import select
    import json
    from pathlib import Path

    with Session(engine_sync) as session:
        # Create roles and permissions
        role_permissions = {
            "Admin": ["users:read", "users:write", "models:write", "audit:read", "customers:read", "predictions:write"],
            "Analyst": ["customers:read", "predictions:write", "models:read", "dashboard:read"],
            "Retention Manager": ["customers:read", "recommendations:write", "campaigns:write", "dashboard:read"],
            "Marketing Manager": ["campaigns:write", "recommendations:read", "dashboard:read"],
        }

        permissions = {}
        for names in role_permissions.values():
            for pname in names:
                existing = session.execute(select(Permission).filter_by(permission_name=pname)).scalar_one_or_none()
                if not existing:
                    perm = Permission(permission_name=pname, description=pname.replace(":", " ").title())
                    session.add(perm)
                    session.flush()
                    permissions[pname] = perm
                else:
                    permissions[pname] = existing

        roles = {}
        for role_name, perm_names in role_permissions.items():
            existing = session.execute(select(Role).filter_by(name=role_name)).scalar_one_or_none()
            if not existing:
                role = Role(name=role_name, description=f"{role_name} platform role")
                session.add(role)
                session.flush()
                roles[role_name] = role
            else:
                roles[role_name] = existing
            for pname in perm_names:
                rp = session.execute(select(RolePermission).filter_by(role_id=roles[role_name].id, permission_id=permissions[pname].id)).scalar_one_or_none()
                if not rp:
                    session.add(RolePermission(role_id=roles[role_name].id, permission_id=permissions[pname].id))

        # Create admin user
        admin_email = settings.FIRST_ADMIN_EMAIL
        existing_admin = session.execute(select(User).filter_by(email=admin_email)).scalar_one_or_none()
        if not existing_admin:
            admin = User(
                email=admin_email,
                full_name=settings.FIRST_ADMIN_NAME,
                password_hash=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                is_active=True,
                email_verified=True,
                role_id=roles["Admin"].id,
            )
            session.add(admin)
            print(f"Admin user created: {admin_email}")

        # Register ML models from metadata
        metadata_path = Path(settings.ML_ARTIFACTS_PATH) / "metadata.json"
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            for model_name in metadata.get("selected_models", []):
                existing_model = session.execute(select(MLModel).filter_by(name=model_name)).scalar_one_or_none()
                if not existing_model:
                    model = MLModel(
                        name=model_name,
                        version=settings.ML_MODEL_VERSION,
                        model_type=model_name,
                        model_path=str(Path(settings.ML_ARTIFACTS_PATH) / f"{model_name}.pkl"),
                        feature_columns=metadata.get("feature_columns", []),
                        accuracy=metadata.get("metrics", {}).get(model_name, {}).get("accuracy"),
                        auc_score=metadata.get("metrics", {}).get(model_name, {}).get("auc_score"),
                        is_active=model_name == metadata.get("selected_models", [None])[0],
                        description="Seeded from local training artifacts",
                    )
                    session.add(model)
                    print(f"ML model registered: {model_name}")

        session.commit()
        print("Database seeded successfully.")


if __name__ == "__main__":
    init_db()
    seed()
