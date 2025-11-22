"""Search module specific exceptions"""

from common.exception import JobSearchError


class SearchError(JobSearchError):
    """Base exception for search related errors."""

    status_code = 500
    detail = "Search operation failed."


class VectorDatabaseError(JobSearchError):
    """Exception raised when vector database operations fail."""

    status_code = 503
    detail = "Vector database is unavailable or operation failed."


class LLMError(JobSearchError):
    """Exception raised when LLM operations fail."""

    status_code = 503
    detail = "Language model service is unavailable or operation failed."


class QueryParsingError(JobSearchError):
    """Exception raised when query parsing fails."""

    status_code = 400
    detail = "Failed to parse query."


class InvalidQueryError(JobSearchError):
    """Exception raised when query is invalid."""

    status_code = 400
    detail = "Invalid query provided."


class NoResultsError(JobSearchError):
    """Exception raised when no results are found."""

    status_code = 404
    detail = "No results found for the query."


class DataValidationError(JobSearchError):
    """Exception raised when data validation fails."""

    status_code = 422
    detail = "Data validation failed."
