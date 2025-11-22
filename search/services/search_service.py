"""Main search service orchestrating query processing and response generation"""

from typing import Any, List, Tuple

from common.logger import get_logger
from common.utils import find_unique_results, sort_results_by_score
from search.config import SearchConfig
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
        """
        try:
            self.logger.info(f"Processing search query: '{query}' (top={top})")

            # Parse query into semantic search and filters
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

            # Perform search
            results = search(semantic_query, filters=filters, limit=top * 3)

            # Get unique results
            unique_jobs = find_unique_results(results)
            sorted_results = sort_results_by_score(unique_jobs)

            # Limit to requested top results
            final_results = sorted_results[:top]

            self.logger.info(f"Found {len(final_results)} unique job results")

            # Generate LLM response
            llm_response = get_llm_response(final_results, query)

            return final_results, llm_response

        except Exception as e:
            self.logger.error(f"Error in search_jobs_and_generate_response: {e}")
            raise


def get_search_service() -> SearchService:
    """Dependency injection function for SearchService

    Returns:
        SearchService instance
    """
    return SearchService()
