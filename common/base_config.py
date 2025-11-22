"""Base configuration settings - Shared across all modules"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base application settings with validation - Only shared settings"""

    # API Keys (shared across all modules)
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    QDRANT_API_KEY: str = Field(..., description="Qdrant cloud API key")
    QDRANT_LOCATION: str = Field(..., description="Qdrant cloud location/URL")

    # Qdrant settings
    COLLECTION_NAME: str = Field(
        default="hybrid_search", description="Qdrant collection name"
    )

    # LLM settings (shared by search and query parsing)
    LLM_TEMPERATURE: float = Field(default=0.3, description="LLM temperature")
    LLM_MAX_TOKENS: int = Field(default=10000, description="LLM max token output")
    LLM_MODEL: str = Field(
        default="gemini-2.5-flash", description="Model used in this project"
    )

    # Logging settings (shared across all modules)
    LOG_LEVEL: str = Field(default="DEBUG", description="Logging Level")
    LOG_TO_FILE: bool = Field(default=False, description="Enable file logging")
    LOG_TO_CONSOLE: bool = Field(default=True, description="Enable console logging")

    # Loading the .env files
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Validators
    @field_validator("QDRANT_API_KEY", "GEMINI_API_KEY")
    @classmethod
    def validate_api_key(cls, v, info):
        """Ensures api keys are not empty"""
        if not v or v.strip() == "":
            raise ValueError(f"{info.field_name} is required but found empty")
        return v.strip()

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper
