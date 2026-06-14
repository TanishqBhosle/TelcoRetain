"""
Async SQLAlchemy database engine and session management for Neon PostgreSQL.
Uses asyncpg driver with connection pooling.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import settings


def _connect_args() -> dict:
    args = {
        "server_settings": {
            "application_name": "telecom-retention-backend",
        },
    }
    if "ssl=require" in settings.DATABASE_URL or "sslmode=require" in settings.DATABASE_URL:
        args["ssl"] = "require"
    return args


# --- Async Engine ---
# Guarded engine creation to allow Alembic imports without asyncpg.
try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,          # Validate connections before use
        pool_recycle=3600,            # Recycle connections every hour
        echo=settings.DEBUG,          # Log SQL in debug mode
        connect_args=_connect_args(),
    )
except Exception:  # pragma: no cover
    # When asyncpg is unavailable (e.g., during Alembic migration generation),
    # set engine to None. Any actual DB usage will raise a clear error.
    engine = None


# --- Session Factory ---
# Guard against a missing engine (e.g., when asyncpg is unavailable for Alembic).
if engine is None:
    # Provide a placeholder that raises a clear error if used.
    def _missing_engine(*_args, **_kwargs):  # pragma: no cover
        raise RuntimeError(
            "Database engine is unavailable because asyncpg is not installed. "
            "Install asyncpg to use the application, or run Alembic with the sync "
            "engine configuration."
        )
    AsyncSessionLocal = _missing_engine  # type: ignore
else:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# --- Declarative Base ---
class Base(DeclarativeBase):
    pass


# --- Session Dependency ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- Health Check ---
async def check_database_connection() -> bool:
    """Verify database connectivity. Used by /health/db endpoint."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
