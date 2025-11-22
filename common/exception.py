"""Base exception classes for the job search application"""

from fastapi import HTTPException


class JobSearchError(Exception):
    """Base exception for all job search related errors."""

    status_code: int = 500
    detail: str = "An unexpected error occurred. Please contact support."

    def __init__(self, message: str | None = None, code: int | None = None) -> None:
        """
        Initialize the JobSearchError.

        Args:
            message: The error message. If None, uses the default detail.
            code: The HTTP status code. If None, uses the default status_code.
        """
        self.message = message or self.detail
        self.code = code or self.status_code
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """
        Convert the JobSearchError to an HTTPException.

        Returns:
            HTTPException: The corresponding HTTPException.
        """
        return HTTPException(
            status_code=self.code,
            detail={
                "message": self.message,
                "code": self.code,
            },
        )

    def __str__(self) -> str:
        """
        Return a string representation of the error.

        Returns:
            str: A formatted error message.
        """
        return f"JobSearchError: {self.message} (Code: {self.code})"


# Configuration Errors
class ConfigurationError(JobSearchError):
    """Exception raised for configuration related errors."""

    status_code = 500
    detail = "Configuration error occurred."


# Data Ingestion Errors
class DataIngestionError(JobSearchError):
    """Exception raised for data ingestion related errors."""

    status_code = 500
    detail = "Data ingestion error occurred."
