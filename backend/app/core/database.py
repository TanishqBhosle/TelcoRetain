"""
Async SQLAlchemy database engine and session management.
Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite) backends.
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


def _build_engine():
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        return create_async_engine(
            url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )
    # PostgreSQL
    connect_args = {
        "server_settings": {
            "application_name": "telecom-retention-backend",
        },
    }
    if "ssl=require" in url or "sslmode=require" in url:
        connect_args["ssl"] = "require"
    return create_async_engine(
        url,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG,
        connect_args=connect_args,
    )


try:
    engine = _build_engine()
except Exception:
    engine = None

if engine is None:
    def _missing_engine(*_args, **_kwargs):
        raise RuntimeError("Database engine is unavailable.")
    AsyncSessionLocal = _missing_engine
else:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
