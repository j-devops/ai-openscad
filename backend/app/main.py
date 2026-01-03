"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import asyncio

from app.config import settings
from app.api.v1 import routes as api_v1_routes
from app.core.cleanup import FileCleanup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cleanup task state
cleanup_task = None
file_cleanup = FileCleanup(max_age_hours=24)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered OpenSCAD code generation and rendering platform"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def cleanup_task_loop():
    """Background task to periodically clean up old files"""
    global cleanup_task
    logger.info("Starting file cleanup background task (runs every hour)")

    while True:
        try:
            # Wait 1 hour between cleanups
            await asyncio.sleep(3600)

            # Run cleanup
            logger.info("Running scheduled file cleanup...")
            result = file_cleanup.cleanup_old_files()

            if result["deleted"] > 0:
                freed_mb = result["freed_bytes"] / (1024 * 1024)
                logger.info(
                    f"Cleanup deleted {result['deleted']} files, "
                    f"freed {freed_mb:.2f}MB"
                )

        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    global cleanup_task

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Create data directories
    data_path = Path(settings.DATA_PATH)
    (data_path / "scad_files").mkdir(parents=True, exist_ok=True)
    (data_path / "renders").mkdir(parents=True, exist_ok=True)
    (data_path / "exports").mkdir(parents=True, exist_ok=True)
    (data_path / "logs").mkdir(parents=True, exist_ok=True)

    logger.info("Data directories initialized")

    # Start cleanup background task
    cleanup_task = asyncio.create_task(cleanup_task_loop())
    logger.info("File cleanup task started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global cleanup_task

    logger.info("Shutting down application")

    # Cancel cleanup task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    })


# Include API routes
app.include_router(api_v1_routes.router, prefix="/api/v1", tags=["api"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
