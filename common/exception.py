"""Custom exceptions for the application"""


class ConfigurationError(Exception):
    """Raised when there's a configuration error"""

    pass


class DataIngestionError(Exception):
    """Raised when there's an error during data ingestion"""

    pass


class VectorDatabaseError(Exception):
    """Raised when there's an error with vector database operations"""

    pass


class SearchError(Exception):
    """Raised when there's an error during search operations"""

    pass


class LLMError(Exception):
    """Raised when there's an error with LLM operations"""

    pass
