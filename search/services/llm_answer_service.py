"""Service for generating LLM-powered responses from search results"""

from datetime import datetime
from typing import Any, List

from api_config import api_config
from common.logger import get_logger
from search.exceptions import LLMError
from search.schemas.job_result import JobResult
from search.schemas.query_response import QueryResponse
from search.services.llm_service import get_llm_response

logger = get_logger(__name__)


class LLMAnswerService:
    """Service for converting search results into LLM-powered responses"""

    def __init__(self):
        self.logger = logger

    def answer(self, search_results: List[Any], query: str) -> QueryResponse:
        """
        Generate a complete query response from search results.

        Args:
            search_results: List of search result points from vector database
            query: Original search query

        Returns:
            QueryResponse with formatted jobs and LLM response

        Raises:
            LLMError: If LLM response generation fails
        """
        self.logger.info(
            f"Generating response for {len(search_results)} search results"
        )

        # Convert search results to JobResult objects
        job_results = self._convert_to_job_results(search_results)

        # Generate LLM response
        try:
            llm_response = get_llm_response(search_results, query)
        except LLMError as e:
            self.logger.warning(f"LLM response generation failed: {e}, using fallback")
            llm_response = self._generate_fallback_response(job_results, query)
        except Exception as e:
            self.logger.error(f"Unexpected error in LLM response: {e}")
            llm_response = self._generate_fallback_response(job_results, query)

        self.logger.info("Response generated successfully")

        return QueryResponse(
            success=True,
            query=query,
            response=llm_response,
            jobs=job_results,
            timestamp=datetime.now().isoformat(),
        )

    def _convert_to_job_results(self, search_results: List[Any]) -> List[JobResult]:
        """
        Convert raw search results to JobResult objects.

        Args:
            search_results: List of search result points

        Returns:
            List of JobResult objects
        """
        job_results = []

        for i, point in enumerate(search_results, 1):
            if not hasattr(point, "payload") or not hasattr(point, "score"):
                self.logger.warning(f"Invalid point structure at index {i}")
                continue

            text = point.payload.get("text", "")
            snippet = (
                text[: api_config.SNIPPET_MAX_LENGTH] + "..."
                if len(text) > api_config.SNIPPET_MAX_LENGTH
                else text
            )

            job_results.append(
                JobResult(
                    rank=i,
                    score=point.score,
                    job_title=point.payload.get(
                        "job_title", api_config.DEFAULT_MISSING_VALUE
                    ),
                    company=point.payload.get(
                        "company", api_config.DEFAULT_MISSING_VALUE
                    ),
                    category=point.payload.get(
                        "category", api_config.DEFAULT_MISSING_VALUE
                    ),
                    location=point.payload.get(
                        "location", api_config.DEFAULT_MISSING_VALUE
                    ),
                    job_level=point.payload.get(
                        "Level", api_config.DEFAULT_MISSING_VALUE
                    ),
                    job_id=point.payload.get(
                        "chunk_id", api_config.DEFAULT_MISSING_VALUE
                    ),
                    publication_date=point.payload.get(
                        "publication_date", api_config.DEFAULT_MISSING_VALUE
                    ),
                    description_snippet=snippet,
                )
            )

        return job_results

    def _generate_fallback_response(
        self, job_results: List[JobResult], query: str
    ) -> str:
        """
        Generate a simple fallback response when LLM fails.

        Args:
            job_results: List of job results
            query: Original query

        Returns:
            Fallback response string
        """
        count = len(job_results)
        if count == 0:
            return f"No jobs found matching '{query}'."
        elif count == 1:
            return f"Found 1 job matching '{query}'. Please review the results below."
        else:
            return f"Found {count} jobs matching '{query}'. The results are sorted by relevance."


def get_llm_answer_service() -> LLMAnswerService:
    """
    Dependency injection function for LLMAnswerService.

    Returns:
        LLMAnswerService instance
    """
    return LLMAnswerService()
