import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation"""

    # .env file validations
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    QDRANT_API_KEY: str = Field(..., description="Qdrat cloud API key")
    QDRANT_LOCATION: str = Field(..., description="Qdrant cloud location/URL")

    # Applicaiton settings

    CSV_FILE_PATH: str = Field(
        default="lf_job.csv",
        description="Path to the csv file (related to project root)",
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
