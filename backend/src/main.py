"""Main FastAPI application for Enterprise Data Intelligence Assistant."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.mongo import close_mongo_connection, connect_to_mongo
from .utils.logger import get_logger
from .startup import run_startup_pipeline

logger = get_logger("backend.main", "/app/logs/backend.api.log")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - startup and shutdown."""
    # Startup
    logger.info(
        "Starting Enterprise Data Intelligence Backend",
        extra={
            "event": "startup_initiated",
            "mongodb_url": settings.MONGODB_URL,
            "llm_service_url": settings.LLM_SERVICE_URL,
            "llm_model": settings.LLM_MODEL,
        },
    )

    try:
        # Connect to MongoDB
        logger.info("Connecting to MongoDB", extra={"event": "mongodb_connection_start"})
        await connect_to_mongo(settings.MONGODB_URL)
        logger.info(
            "Successfully connected to MongoDB",
            extra={"event": "mongodb_connection_success", "mongodb_url": settings.MONGODB_URL},
        )
    except Exception as e:
        logger.error(
            f"Failed to connect to MongoDB: {e}",
            extra={
                "event": "mongodb_connection_failed",
                "error": str(e),
                "mongodb_url": settings.MONGODB_URL,
            },
        )
        raise

    # Run startup pipeline (scraping and analysis)
    logger.info("Starting automatic scraping and analysis", extra={"event": "pipeline_trigger"})
    try:
        await run_startup_pipeline()
    except Exception as e:
        logger.error(
            f"Startup pipeline failed, but backend will continue: {e}",
            extra={"event": "pipeline_error", "error": str(e)},
        )

    logger.info(
        "Backend startup complete - ready to accept requests",
        extra={"event": "startup_complete", "status": "healthy"},
    )

    yield

    # Shutdown
    logger.info("Shutting down backend", extra={"event": "shutdown_initiated"})

    try:
        await close_mongo_connection()
        logger.info(
            "Successfully closed MongoDB connection",
            extra={"event": "mongodb_connection_closed"},
        )
    except Exception as e:
        logger.warning(
            f"Error during MongoDB connection cleanup: {e}",
            extra={"event": "mongodb_cleanup_error", "error": str(e)},
        )

    logger.info("Backend shutdown complete", extra={"event": "shutdown_complete"})


# Create FastAPI application
app = FastAPI(
    title="Enterprise Data Intelligence API",
    description="REST API for intelligence gathering system - articles, entities, and statistics",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "service": "Enterprise Data Intelligence API",
        "version": "1.0.0",
        "status": "running",
    }


# Import and include routers
from .api.routes import health, articles

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(articles.router, prefix="/api", tags=["articles"])

# Additional routers (will be added in Phase 6)
# from .api.routes import stats, entities
# app.include_router(stats.router, prefix="/api", tags=["stats"])
# app.include_router(entities.router, prefix="/api", tags=["entities"])
