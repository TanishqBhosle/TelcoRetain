"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables from SQLAlchemy metadata."""
    bind = op.get_bind()
    from app.models import Base

    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop tables from SQLAlchemy metadata."""
    bind = op.get_bind()
    from app.models import Base

    Base.metadata.drop_all(bind=bind)
