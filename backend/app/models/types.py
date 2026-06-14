"""Database type compatibility for PostgreSQL and SQLite backends."""
from sqlalchemy import String, JSON, TypeDecorator
from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Use JSON for both backends
JSONB = JSON


class UUIDCompat(TypeDecorator):
    """UUID type that stores as String on SQLite, native UUID on PostgreSQL."""
    impl = String(36)
    cache_ok = True

    def __init__(self, as_uuid=False, *args, **kwargs):
        self.as_uuid = as_uuid
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value) if self.as_uuid else value
        return value

    def process_result_value(self, value, dialect):
        if value is not None and self.as_uuid:
            import uuid as _uuid
            return _uuid.UUID(value) if not isinstance(value, _uuid.UUID) else value
        return value


UUID = UUIDCompat
