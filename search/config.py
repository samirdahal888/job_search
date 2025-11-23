"""Search module configuration"""

from common.config.base_config import BaseConfig
from pydantic import Field, field_validator


class SearchConfig(BaseConfig):
    """Configuration for search module - inherits all from base"""
    # API Keys (shared across all modules)
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")

    # LLM settings (shared by search and query parsing)
    LLM_TEMPERATURE: float = Field(default=0.3, description="LLM temperature")
    LLM_MAX_TOKENS: int = Field(default=10000, description="LLM max token output")
    LLM_MODEL: str = Field(
        default="gemini-2.5-flash", description="Model used in this project"
    )

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

    # Validators
    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_api_key(cls, v):
        """Ensures API key is not empty"""
        if not v or not v.strip():
            raise ValueError("GEMINI_API_KEY is required but found empty")
        return v.strip()
    


