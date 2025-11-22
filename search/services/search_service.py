"""Main search service orchestrating query processing and response generation"""

from typing import Any, List, Tuple

from common.logger import get_logger
from common.utils import find_unique_results, sort_results_by_score
from search.config import SearchConfig
from search.exceptions import LLMError, SearchError, VectorDatabaseError
from search.services.llm_service import get_llm_response
from search.services.query_parser import convert_query_to_semantic_and_filter
from search.services.vector_search import create_filter_object, search

config = SearchConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)


class SearchService:
    """Service class to handle job search business logic"""

    def __init__(self):
        self.logger = logger

    def search_jobs_and_generate_response(
        self, query: str, top: int
    ) -> Tuple[List[Any], str]:
        """
        Search for jobs based on query and generate AI-powered response.

        Args:
            query: The search query string
            top: Maximum number of results to return

        Returns:
            Tuple of (job_results, llm_response)

        Raises:
            SearchError: If search operation fails
            VectorDatabaseError: If vector database operation fails
        """
        # Principle 3: Validate inputs to prevent exceptions
        if not query or not query.strip():
            self.logger.error("Empty query provided to search service")
            raise SearchError("Query cannot be empty")

        if top <= 0:
            self.logger.warning(f"Invalid top value {top}, using default 3")
            top = 3

        self.logger.info(f"Processing search query: '{query}' (top={top})")

        # Parse query into semantic search and filters
        # Query parser handles its own exceptions
        parsed_query = convert_query_to_semantic_and_filter(query)

        if not parsed_query:
            self.logger.warning("Query parsing failed, using original query")
            semantic_query = query
            filters = None
        else:
            semantic_query = parsed_query.get("semantic_query", query)
            filter_dict = parsed_query.get("filters", {})
            filters = create_filter_object(filter_dict) if filter_dict else None

        self.logger.debug(f"Semantic query: {semantic_query}")
        self.logger.debug(f"Filters: {filter_dict if parsed_query else 'None'}")

        # Principle 2: Use specific exception handling, not catch-all
        try:
            # Perform search - can raise VectorDatabaseError
            results = search(semantic_query, filters=filters, limit=top * 3)
        except VectorDatabaseError:
            # Re-raise specific vector database errors
            raise
        except Exception as e:
            # Only catch truly unexpected errors
            self.logger.error(f"Unexpected error during vector search: {e}")
            raise SearchError(f"Search operation failed: {str(e)}") from e

        # Principle 3: Validate results before processing
        if results is None:
            self.logger.error("Vector search returned None")
            raise SearchError("Search operation returned invalid results")

        if not isinstance(results, list):
            self.logger.error(f"Invalid search results type: {type(results)}")
            raise SearchError("Search operation returned invalid result type")

        # Get unique results
        unique_jobs = find_unique_results(results)
        sorted_results = sort_results_by_score(unique_jobs)

        # Limit to requested top results
        final_results = sorted_results[:top]

        self.logger.info(f"Found {len(final_results)} unique job results")

        # Generate LLM response - use fallback on failure
        try:
            llm_response = get_llm_response(final_results, query)
        except LLMError as e:
            # Principle 2: Don't control flow with exceptions, but provide fallback
            self.logger.warning(f"LLM response generation failed: {e}, using fallback")
            llm_response = self._generate_fallback_response(final_results, query)
        except Exception as e:
            self.logger.error(f"Unexpected error in LLM response: {e}")
            llm_response = self._generate_fallback_response(final_results, query)

        return final_results, llm_response

    def _generate_fallback_response(self, results: List[Any], query: str) -> str:
        """Generate a simple fallback response when LLM fails

        Args:
            results: Search results
            query: Original query

        Returns:
            Fallback response string
        """
        count = len(results)
        if count == 0:
            return f"No jobs found matching '{query}'."
        elif count == 1:
            return f"Found 1 job matching '{query}'. Please review the results below."
        else:
            return f"Found {count} jobs matching '{query}'. The results are sorted by relevance."


def get_search_service() -> SearchService:
    """Dependency injection function for SearchService

    Returns:
        SearchService instance
    """
    return SearchService()
