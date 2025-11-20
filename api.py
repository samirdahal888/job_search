from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from config import settings
from logger import get_logger
from search_service import SearchService, get_search_service

logger = get_logger(__name__)

app = FastAPI(
    title="RAG Application for Job search",
    description="Intelligent job search using Retrieval-Augmented Generation",
    version="0.1",
    redoc_url="/redocs",
)


class QueryRequest(BaseModel):
    query: str = Field(max_length=120, min_length=2)
    top: int = Field(
        default=settings.DEFAULT_QUERY_RESULT, ge=1, le=settings.MAX_QUERY_RESULT
    )


class JobResult(BaseModel):
    rank: int
    score: float
    job_title: str
    company: str
    category: str
    location: Optional[str] = None
    job_level: str
    job_id: str
    publication_date: Optional[str] = None
    description_snippet: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for job search query"""

    success: bool
    query: str
    response: str
    jobs: List[JobResult]
    timestamp: str


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


@app.post("/api/query", response_model=QueryResponse, tags=["Query"])
def job_query(
    request: QueryRequest, search_service: SearchService = Depends(get_search_service)
):
    """
    Search for jobs using natural language query.

    Args:
        request: Query request containing search query and result limit
        search_service: Injected search service dependency

    Returns:
        QueryResponse with matching jobs and LLM-generated response
    """
    unique_results, response_from_llm = (
        search_service.search_jobs_and_generate_response(request.query, request.top)
    )

    job_result = []
    for i, point in enumerate(unique_results, 1):
        text = point.payload.get("text", "")
        snippet = (
            text[: settings.SNIPPET_MAX_LENGTH] + "..."
            if len(text) > settings.SNIPPET_MAX_LENGTH
            else text
        )

        job_result.append(
            JobResult(
                rank=i,
                score=point.score,
                job_title=point.payload.get(
                    "job_title", settings.DEFAULT_MISSING_VALUE
                ),
                company=point.payload.get("company", settings.DEFAULT_MISSING_VALUE),
                category=point.payload.get("category", settings.DEFAULT_MISSING_VALUE),
                location=point.payload.get("location", settings.DEFAULT_MISSING_VALUE),
                job_level=point.payload.get("Level", settings.DEFAULT_MISSING_VALUE),
                job_id=point.payload.get("chunk_id", settings.DEFAULT_MISSING_VALUE),
                publication_date=point.payload.get("publication_date",settings.DEFAULT_MISSING_VALUE),
                description_snippet=snippet,
            )
        )

    logger.info(f"Query processed successfully, returning {len(job_result)} jobs")

    return QueryResponse(
        success=True,
        query=request.query,
        response=response_from_llm,
        jobs=job_result,
        timestamp=datetime.now().isoformat(),
    )
