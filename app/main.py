"""
Application entry point.
Configures and starts the FastAPI server.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Adjust imports to use app package
from app.core.config import get_settings
from app.core.logger import Logger
from app.api.routes import router

settings = get_settings()
logger = Logger("main")


def create_application() -> FastAPI:
    """Application factory function."""
    
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Universal Smart Assistant for E-commerce and Entertainment",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    application.include_router(router)
    
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    """Application startup handler."""
    logger.info(f"{settings.app_name} v{settings.app_version} starting...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown handler."""
    logger.info("Application shutting down...")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )