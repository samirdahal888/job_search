"""Search API router"""

from datetime import datetime

from fastapi import APIRouter, Depends

from api_config import api_config
from common.logger import get_logger
from search.exceptions import SearchError
from search.schemas.job_result import JobResult
from search.schemas.query_request import QueryRequest
from search.schemas.query_response import QueryResponse
from search.services.search_service import SearchService, get_search_service

logger = get_logger(__name__)

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

    Raises:
        InvalidQueryError: If query is empty or invalid
        SearchError: If search operation fails
    """
    logger.info(f"Processing query: '{request.query}' (top={request.top})")

    unique_results, response_from_llm = (
        search_service.search_jobs_and_generate_response(request.query, request.top)
    )

    if unique_results is None:
        logger.error("Search service returned None for unique_results")
        raise SearchError("Search operation returned invalid results")

    if not isinstance(unique_results, list):
        logger.error(f"Invalid result type: {type(unique_results)}")
        raise SearchError("Search operation returned invalid result type")

    job_result = []
    for i, point in enumerate(unique_results, 1):
        # Principle 3: Validate point has required attributes
        if not hasattr(point, "payload") or not hasattr(point, "score"):
            logger.warning(f"Invalid point structure at index {i}")
            continue

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
