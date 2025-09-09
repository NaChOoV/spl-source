from fastapi import FastAPI
from config.env import config
from app.controllers import (
    access_controller,
    health_controller,
    user_controller,
)
import logging
from contextlib import asynccontextmanager

from app.services.source_service import SourceService

source_service = SourceService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await source_service.login()
    yield
    # Shutdown (if needed)
    # await source_service.logout()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application

    Returns:
        FastAPI: Configured application instance
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = FastAPI(
        title=config.API_TITLE,
        version=config.API_VERSION,
        description=config.API_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Include routers
    app.include_router(health_controller.router)
    app.include_router(user_controller.router)
    app.include_router(access_controller.router)

    return app


# Create the app instance
app = create_app()
