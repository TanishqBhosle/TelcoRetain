"""
Alembic environment configuration for async SQLAlchemy models.
This file is used by Alembic commands (e.g., `alembic upgrade head`).
It imports the Base metadata from `app.models` so that autogeneration
detects all tables defined in the project.
"""
import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------------------------------------
# Add the project's model path so Alembic can discover tables.
# ----------------------------------------------------------------------
# Import the Base that holds the model metadata.
from app.models import Base  # noqa: F401

# target_metadata is the MetaData object that Alembic will use for
# "autogenerate" support.
target_metadata = Base.metadata

# ----------------------------------------------------------------------
# Helper to run migrations in async mode.
# ----------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    In this context we don't need an actual DB connection; Alembic
    just produces SQL scripts.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations in 'online' mode with an async engine."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    Uses a synchronous SQLAlchemy engine via the sync_database_url from settings.
    This avoids the asyncpg dependency during migration generation.
    """
    try:
        from app.core.config import settings
        url = settings.sync_database_url
    except Exception:
        # Fallback to the URL from alembic.ini if settings import fails
        url = config.get_main_option("sqlalchemy.url")

    # Create a sync engine
    from sqlalchemy import create_engine
    connectable = create_engine(url, future=True)

    # Run migrations within the sync engine context
    with connectable.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# ----------------------------------------------------------------------
# Determine whether we are running in offline or online mode.
# ----------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
