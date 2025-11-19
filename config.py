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
    COLLECTION_NAME: str =Field(
        default="hybrid_search",
        description="Qdrant collection name"
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # API settings
    API_HOST:str = Field(default='0.0.0.0',description="API host")
    API_port:int = Field(default=8000,description="API port")
    MAX_QUERY_RESULT: int = Field(default=20,description="Maximum number of result for a query")
    DEFAULT_QUERY_RESULT: int =Field(default=3,description="Default number of result per query")

    # chunks related  settings 

    CHUNK_SIZE:int =Field(default=300,description='Text chunk size for splitting')
    CHUNK_OVERLAP: int = Field(default=30,description="overlap between chunks")


settings = Settings()
