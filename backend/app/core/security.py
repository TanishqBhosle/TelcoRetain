"""
Security utilities: JWT token management, bcrypt hashing, token blacklisting.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings
import redis.asyncio as aioredis
import structlog

logger = structlog.get_logger(__name__)

# --- Redis client (optional) ---
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    """Returns Redis client if configured, else None (in-memory fallback)."""
    global _redis_client
    if _redis_client is None and settings.REDIS_URL:
        try:
            _redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await _redis_client.ping()
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            _redis_client = None
    return _redis_client


# In-memory token blacklist fallback
_blacklisted_tokens: set[str] = set()


# ==============================================================
# Password Utilities
# ==============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ==============================================================
# JWT Token Creation
# ==============================================================

def create_access_token(
    subject: str,
    role: str,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create a JWT access token.
    - subject: user UUID
    - role: user role name
    - expires in: ACCESS_TOKEN_EXPIRE_MINUTES
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a JWT refresh token.
    - expires in: REFRESH_TOKEN_EXPIRE_DAYS
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ==============================================================
# JWT Token Verification
# ==============================================================

def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError on invalid/expired tokens.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ==============================================================
# Token Blacklist (Logout)
# ==============================================================

async def blacklist_token(token: str, expire_seconds: int = 3600) -> None:
    """Add a token to the blacklist (logout)."""
    redis = await get_redis()
    if redis:
        await redis.setex(f"blacklist:{token}", expire_seconds, "1")
    else:
        _blacklisted_tokens.add(token)


async def is_token_blacklisted(token: str) -> bool:
    """Check if a token has been blacklisted."""
    redis = await get_redis()
    if redis:
        return bool(await redis.exists(f"blacklist:{token}"))
    return token in _blacklisted_tokens


# ==============================================================
# Email Verification Token
# ==============================================================

def create_verification_token(email: str) -> str:
    """Create a short-lived email verification token (24h)."""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": email,
        "type": "email_verify",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_password_reset_token(email: str) -> str:
    """Create a short-lived password reset token (15 min)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "sub": email,
        "type": "password_reset",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
