"""Search API router"""

from fastapi import APIRouter, Depends

from common.logger import get_logger
from search.exceptions import SearchError
from search.schemas.query_request import QueryRequest
from search.schemas.query_response import QueryResponse
from search.services.llm_answer_service import LLMAnswerService, get_llm_answer_service
from search.services.search_service import SearchService, get_search_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["Search"])


@router.post("/query", response_model=QueryResponse)
def job_query(
    request: QueryRequest,
    search_service: SearchService = Depends(get_search_service),
    llm_answer_service: LLMAnswerService = Depends(get_llm_answer_service),
) -> QueryResponse:
    """
    Search for jobs using natural language query.

    Args:
        request: Query request containing search query and result limit
        search_service: Injected search service dependency
        llm_answer_service: Injected LLM answer service dependency

    Returns:
        QueryResponse with matching jobs and LLM-generated response

    Raises:
        InvalidQueryError: If query is empty or invalid
        SearchError: If search operation fails
    """
    logger.info(f"Processing query: '{request.query}' (top={request.top})")

    # Get search results
    search_results = search_service.search(request.query, request.top)

    if search_results is None:
        logger.error("Search service returned None")
        raise SearchError("Search operation returned invalid results")

    if not isinstance(search_results, list):
        logger.error(f"Invalid result type: {type(search_results)}")
        raise SearchError("Search operation returned invalid result type")

    # Generate complete response with LLM
    response = llm_answer_service.answer(search_results, request.query)

    logger.info(f"Query processed successfully, returning {len(response.jobs)} jobs")

    return response
