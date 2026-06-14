"""
Rate Limiting Middleware.
Implements sliding-window rate limiting using Redis with an in-memory fallback.
Supports separate limit rates for Authentication, Predictions, and general routes.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.security import get_redis
import structlog

logger = structlog.get_logger(__name__)

# In-memory fallback dictionary for sliding window timestamps
# Structure: { key: [timestamps] }
_in_memory_limits: dict[str, list[float]] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks request counts per user (or client IP)
    and enforces rate limits based on path prefix.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Bypasses health checks to avoid false alarms
        if path.startswith("/health") or path == "/":
            return await call_next(request)

        # 1. Resolve identifier key (User ID if authenticated, else IP)
        user = getattr(request.state, "user", None)
        if user:
            key_identifier = f"user:{user.id}"
        else:
            client_ip = request.client.host if request.client else "unknown"
            key_identifier = f"ip:{client_ip}"

        # 2. Parse configurations for limits (default window is 60 seconds)
        # Parse rate limit configuration string, e.g. "10/minute" -> limit=10, window=60
        limit_str = settings.RATE_LIMIT_DEFAULT
        if "/auth" in path:
            limit_str = settings.RATE_LIMIT_AUTH
        elif "/predict" in path:
            limit_str = settings.RATE_LIMIT_PREDICTION

        try:
            limit_part, window_part = limit_str.split("/")
            limit = int(limit_part)
            if "minute" in window_part:
                window = 60
            elif "hour" in window_part:
                window = 3600
            elif "day" in window_part:
                window = 86400
            else:
                window = 60
        except Exception:
            limit = 120
            window = 60

        rate_limit_key = f"ratelimit:{key_identifier}:{path}"
        redis = await get_redis()
        current_time = time.time()

        if redis:
            try:
                # Sliding window using Redis Sorted Sets
                pipe = redis.pipeline()
                # Clear expired requests
                pipe.zremrangebyscore(rate_limit_key, 0, current_time - window)
                # Count current requests in window
                pipe.zcard(rate_limit_key)
                # Add current request timestamp
                pipe.zadd(rate_limit_key, {str(current_time): current_time})
                # Refresh key TTL
                pipe.expire(rate_limit_key, window)
                
                results = await pipe.execute()
                request_count = results[1]

                if request_count > limit:
                    logger.warning("rate_limit_exceeded", identifier=key_identifier, path=path, limit=limit_str)
                    return JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "message": "Rate limit exceeded. Please try again later.",
                            "data": None
                        }
                    )
            except Exception as e:
                logger.error("redis_rate_limiter_error", error=str(e))
                # Log error and fallback to in-memory implementation
                if await self._check_in_memory_limit(rate_limit_key, limit, window, current_time):
                    return JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "message": "Rate limit exceeded. Please try again later.",
                            "data": None
                        }
                    )
        else:
            # Fallback to in-memory sliding window
            if await self._check_in_memory_limit(rate_limit_key, limit, window, current_time):
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded. Please try again later.",
                        "data": None
                    }
                )

        return await call_next(request)

    async def _check_in_memory_limit(
        self, key: str, limit: int, window: int, current_time: float
    ) -> bool:
        """Helper to compute sliding window rate limit in memory."""
        timestamps = _in_memory_limits.get(key, [])
        # Filter out timestamps older than the sliding window
        cutoff = current_time - window
        timestamps = [t for t in timestamps if t > cutoff]
        
        if len(timestamps) >= limit:
            logger.warning("rate_limit_exceeded_in_memory", key=key, limit=limit)
            return True
            
        timestamps.append(current_time)
        _in_memory_limits[key] = timestamps
        return False
