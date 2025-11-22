"""API factory for creating FastAPI application"""

from fastapi import FastAPI

from api_config import api_config
from common.logger import get_logger
from search.routers.search import router as search_router

logger = get_logger(
    __name__, api_config.LOG_LEVEL, api_config.LOG_TO_CONSOLE, api_config.LOG_TO_FILE
)


def create_app() -> FastAPI:
    """Create and configure FastAPI application

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="RAG Application for Job search",
        description="Intelligent job search using Retrieval-Augmented Generation",
        version="0.1",
        redoc_url="/redocs",
    )

    # Include routers
    app.include_router(search_router)

    @app.get("/", tags=["Root"])
    def root():
        logger.debug("Home endpoint accessed")
        return {
            "message": "LF Jobs RAG API",
            "version": 0.1,
            "description": "Intelligent job search using Retrieval-Augmented Generation",
            "endpoints": {
                "POST /api/query": "Search for jobs with natural language",
            },
        }

    logger.info("FastAPI application created successfully")
    return app
