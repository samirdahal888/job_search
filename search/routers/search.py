"""Search API router"""

from datetime import datetime

from fastapi import APIRouter, Depends

from api_config import api_config
from common.logger import get_logger
from search.config import SearchConfig
from search.schemas.job_result import JobResult
from search.schemas.query_request import QueryRequest
from search.schemas.query_response import QueryResponse
from search.services.search_service import SearchService, get_search_service

config = SearchConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)

router = APIRouter(prefix="/api", tags=["Search"])


@router.post("/query", response_model=QueryResponse)
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
            text[: api_config.SNIPPET_MAX_LENGTH] + "..."
            if len(text) > api_config.SNIPPET_MAX_LENGTH
            else text
        )

        job_result.append(
            JobResult(
                rank=i,
                score=point.score,
                job_title=point.payload.get(
                    "job_title", api_config.DEFAULT_MISSING_VALUE
                ),
                company=point.payload.get("company", api_config.DEFAULT_MISSING_VALUE),
                category=point.payload.get(
                    "category", api_config.DEFAULT_MISSING_VALUE
                ),
                location=point.payload.get(
                    "location", api_config.DEFAULT_MISSING_VALUE
                ),
                job_level=point.payload.get("Level", api_config.DEFAULT_MISSING_VALUE),
                job_id=point.payload.get("chunk_id", api_config.DEFAULT_MISSING_VALUE),
                publication_date=point.payload.get(
                    "publication_date", api_config.DEFAULT_MISSING_VALUE
                ),
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
