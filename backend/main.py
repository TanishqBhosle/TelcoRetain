"""
Telecom Customer Retention Intelligence Platform
FastAPI Application Entry Point
"""

import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import check_database_connection, engine
from app.core.logging import setup_logging
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.exceptions.handlers import register_exception_handlers
from app.middleware import AuthMiddleware, RateLimitMiddleware, AuditMiddleware
from app.routes import api_router
from ml.inference.artifact_loader import ArtifactRegistry
from ml.explainability.shap_explainer import SHAPExplainer

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Telecom Customer Retention Intelligence Platform")

    # Check database connection
    try:
        db_connected = await check_database_connection()
        if db_connected:
            logger.info("Database connection established")
        else:
            logger.error("Failed to connect to database")
            raise RuntimeError("Database connection failed")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

    # Initialize ML artifacts
    try:
        ArtifactRegistry.initialize(Path(settings.ML_MODELS_PATH))
        if ArtifactRegistry.is_loaded():
            logger.info("ML artifacts loaded successfully")
            SHAPExplainer.initialize()
            logger.info("SHAP explainer initialized")
        else:
            logger.warning("ML artifacts not fully loaded. Continuing without ML inference.")
    except Exception as e:
        logger.warning(f"ML artifacts not loaded: {e}. Continuing without ML inference.")

    # Start APScheduler for background jobs
    start_scheduler()
    logger.info("Background job scheduler started")

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down application")

    # Stop scheduler
    shutdown_scheduler()

    # Close database engine
    await engine.dispose()
    logger.info("Database connections closed")

    # Cleanup ML resources
    ArtifactRegistry.cleanup()
    logger.info("ML resources cleaned up")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Telecom Customer Retention Intelligence Platform with ML-powered churn prediction",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - executed in reverse order)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Register standard exception envelopes
register_exception_handlers(app)


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db", tags=["health"])
async def database_health_check():
    """Database connectivity health check."""
    is_connected = await check_database_connection()
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "component": "database",
        "connected": is_connected
    }


@app.get("/health/ml", tags=["health"])
async def ml_health_check():
    """ML models health check."""
    try:
        models_loaded = ArtifactRegistry.is_loaded()
        metadata = ArtifactRegistry.get_metadata() if models_loaded else {}
        return {
            "status": "healthy" if models_loaded else "degraded",
            "component": "ml_models",
            "models_loaded": models_loaded,
            "metadata": metadata,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "component": "ml_models",
            "error": str(e)
        }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
