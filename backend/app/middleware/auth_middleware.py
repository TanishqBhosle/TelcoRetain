"""
JWT Authentication Middleware.
Extracts token from Authorization header, validates claims, checks blacklist,
and attaches active database User object to request.state.user.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token, is_token_blacklisted
from app.models.users import User
import structlog

logger = structlog.get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to populate request.state.user based on a valid JWT token."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.user = None
        request.state.token = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            try:
                # 1. Check blacklist
                if not await is_token_blacklisted(token):
                    # 2. Decode JWT
                    payload = decode_token(token)
                    user_id_str = payload.get("sub")
                    
                    if user_id_str:
                        user_id = uuid.UUID(user_id_str)
                        
                        # 3. Retrieve user from database
                        async with AsyncSessionLocal() as session:
                            stmt = select(User).where(User.id == user_id)
                            result = await session.execute(stmt)
                            user = result.scalar_one_or_none()
                            
                            if user and user.is_active and not user.is_locked:
                                request.state.user = user
                                request.state.token = token
            except Exception as e:
                # Log at debug level to avoid log pollution from expired/invalid tokens
                logger.debug("auth_middleware_token_failed", error=str(e))

        response = await call_next(request)
        return response
