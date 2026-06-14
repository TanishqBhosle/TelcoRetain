"""Audit middleware.

- Logs each authenticated request to the ``audit_logs`` table.
- Captures user ID (if any), HTTP method, path, timestamp, request body (truncated), and response status.
- Uses the async session from ``app.core.database``.
- Intended for low-overhead audit trails; does not log response bodies.
"""

import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import AsyncSessionLocal
from app.models.audit import AuditLog

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that records an ``AuditLog`` entry for every request.

    The middleware runs after authentication (so ``request.state.user`` may be set).
    If the request is unauthenticated ``user_id`` will be ``None``.
    """

    async def dispatch(self, request: Request, call_next):
        # Capture request details before processing
        method = request.method
        path = request.url.path
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        # Read request body (limit to 1 KB for privacy)
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="ignore")
        truncated_body = (body_str[:1024] + "...") if len(body_str) > 1024 else body_str

        # Process the request
        response: Response = await call_next(request)

        # Determine user ID from AuthMiddleware (if set)
        user = getattr(request.state, "user", None)
        user_id = str(user.id) if user else None

        # Persist audit entry asynchronously
        try:
            async with AsyncSessionLocal() as session:
                audit_entry = AuditLog(
                    user_id=user.id if user else None,
                    action="request",
                    resource_type="endpoint",
                    resource_id=path,
                    request_payload={"body": truncated_body},
                    response_status=response.status_code,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("User-Agent"),
                    additional_data={"method": method},
                )
                session.add(audit_entry)
                await session.commit()
        except Exception:
            pass

        return response
