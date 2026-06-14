"""
Global exception handlers.
Formats errors to match the standard API response wrapper:
{"success": false, "message": "error description", "data": null, "timestamp": "...", "path": "..."}
"""

import datetime
import logging
from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.custom import PlatformException

logger = logging.getLogger(__name__)


def format_error_response(request: Request, status_code: int, message: str, data: Any = None) -> JSONResponse:
    """Helper to structure error envelopes consistently."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": data,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "path": request.url.path,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers standard and custom exception handlers on the FastAPI app."""

    @app.exception_handler(PlatformException)
    async def platform_exception_handler(request: Request, exc: PlatformException) -> JSONResponse:
        logger.warning(
            "platform_exception",
            path=request.url.path,
            status_code=exc.status_code,
            message=exc.message,
        )
        return format_error_response(request, exc.status_code, exc.message, exc.data)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Format errors into a readable structure
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Validation error")
            errors.append(f"[{loc}]: {msg}")
            
        message = "Validation failed: " + "; ".join(errors)
        logger.info("validation_error", path=request.url.path, errors=errors)
        
        return format_error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            message,
            data={"errors": exc.errors()},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.info(
            "http_exception",
            path=request.url.path,
            status_code=exc.status_code,
            message=exc.detail,
        )
        return format_error_response(request, exc.status_code, exc.detail)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_server_error", path=request.url.path, error=str(exc))
        return format_error_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected server error occurred.",
        )
