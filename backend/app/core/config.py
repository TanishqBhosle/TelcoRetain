"""
Application configuration using Pydantic Settings.
All values loaded from environment variables or .env file.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "Telecom Customer Retention Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/telco_retain"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # --- JWT Security ---
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-MINIMUM-32-CHARS"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Redis ---
    REDIS_URL: Optional[str] = None

    # --- CORS ---
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",")]
        return v

    # --- Rate Limiting ---
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_PREDICTION: str = "60/minute"
    RATE_LIMIT_DEFAULT: str = "120/minute"

    # --- ML Artifacts ---
    ML_ARTIFACTS_PATH: str = "./ml/artifacts"
    ML_MODEL_VERSION: str = "v1.0"

    # --- Email ---
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@telecom-retention.com"
    EMAIL_VERIFICATION_REQUIRED: bool = False

    # --- Admin Bootstrap ---
    FIRST_ADMIN_EMAIL: str = "admin@telecom-retention.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@1234"
    FIRST_ADMIN_NAME: str = "System Admin"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT in ("development", "dev", "local")

    @property
    def sync_database_url(self) -> str:
        """Synchronous URL for Alembic migrations."""
        return self.DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        ).replace("?ssl=require", "?sslmode=require")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
