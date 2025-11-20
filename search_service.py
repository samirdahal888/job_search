from typing import Any, Dict, List, Optional, Tuple

from llm_response import get_llm_response
from logger import get_logger
from query_to_semantic_and_filter import convert_query_to_semantic_and_filter
from job_result_processor import (
    find_unique_results,
    sort_results_by_score,
)
from retrieve_data_based_on_query import create_filter_object, search

logger = get_logger(__name__)


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
            Tuple of (unique_results, llm_response)
        """
        self.logger.info(f"Processing query: {query}, top: {top}")

        # Convert query to semantic and filter components
        semantic_query, filters = self._parse_query_into_semantic_and_filters(query)

        self.logger.debug(f"Semantic query: {semantic_query}")
        self.logger.debug(f"Filters: {filters}")

        # Apply filters and search
        filtered_value = create_filter_object(filters)
        results = search(semantic_query, filtered_value, limit=top)

        # Remove duplicates and sort
        unique_outputs = find_unique_results(
            results
        )  # its work is find the unique results
        unique_results = sort_results_by_score(
            unique_outputs
        )  # its work is sort based on score
        self.logger.info(f"Found {len(unique_results)} unique jobs")

        # Generate LLM response
        response_from_llm = get_llm_response(unique_results, query)

        return unique_results, response_from_llm

    def _parse_query_into_semantic_and_filters(
        self, query: str
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Parse user query and separate into semantic search terms and filter criteria.

        Args:
            query: The search query string

        Returns:
            Tuple of (semantic_query, filters)
        """
        data = convert_query_to_semantic_and_filter(query)
        semantic_query = None
        filters = None

        for key, value in data.items():
            if key == "semantic_query":
                semantic_query = value
            elif key == "filters":
                filters = value

        return semantic_query, filters


def get_search_service() -> SearchService:
    """
    Dependency injection function for SearchService.

    Returns:
        SearchService instance
    """
    return SearchService()
