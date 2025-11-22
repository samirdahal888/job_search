"""API configuration"""

from pydantic import Field

from common.base_config import BaseConfig


class APIConfig(BaseConfig):
    """Configuration for the API - API-specific settings"""

    # API server settings
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")

    # Search result settings
    MAX_QUERY_RESULT: int = Field(
        default=20, description="Maximum number of results for a query"
    )
    DEFAULT_QUERY_RESULT: int = Field(
        default=3, description="Default number of results per query"
    )
    SNIPPET_MAX_LENGTH: int = Field(
        default=300, description="Maximum length of job description snippet"
    )
    DEFAULT_MISSING_VALUE: str = Field(
        default="N/A", description="Default value for missing or unavailable data"
    )


# Global config instance
api_config = APIConfig()
