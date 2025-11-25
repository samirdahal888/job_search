"""Main search service orchestrating query processing"""

from typing import Any, List

from common.logger import get_logger
from common.utils.find_unique_results import find_unique_results
from common.utils.sort_results_by_score import sort_results_by_score
from search.config import SearchConfig
from search.exceptions import SearchError, VectorDatabaseError
from search.services.query_parser import convert_query_to_semantic_and_filter
from search.services.vector_search import create_filter_object, search

config = SearchConfig()
logger = get_logger(__name__)


class SearchService:
    """Service class to handle job search business logic"""

    def __init__(self):
        self.logger = logger

    def search(self, query: str, top: int) -> List[Any]:
        """
        Search for jobs based on query.

        Args:
            query: The search query string
            top: Maximum number of results to return

        Returns:
            List of job search results

        Raises:
            SearchError: If search operation fails
            VectorDatabaseError: If vector database operation fails
        """
        if not query or not query.strip():
            self.logger.error("Empty query provided to search service")
            raise SearchError("Query cannot be empty")

        if top <= 0:
            self.logger.warning(f"Invalid top value {top}, using default 3")
            top = 3

        self.logger.info(f"Processing search query: '{query}' (top={top})")

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

        try:
            results = search(semantic_query, filters=filters, limit=top * 3)
        except VectorDatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during vector search: {e}")
            raise SearchError(f"Search operation failed: {str(e)}") from e

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

        return final_results


def get_search_service() -> SearchService:
    """Dependency injection function for SearchService

    Returns:
        SearchService instance
    """
    return SearchService()
