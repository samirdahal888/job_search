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
        default="/home/samir-dahal/leapfrog_job_search/lf_job.csv",
        description="Path to the csv file (related to project root)",
    )
    COLLECTION_NAME: str = Field(
        default="hybrid_search", description="Qdrant collection name"
    )

    # loading the .env files
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # API settings
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_port: int = Field(default=8000, description="API port")
    MAX_QUERY_RESULT: int = Field(
        default=20, description="Maximum number of result for a query"
    )
    DEFAULT_QUERY_RESULT: int = Field(
        default=3, description="Default number of result per query"
    )

    # chunks related  settings
    CHUNK_SIZE: int = Field(default=300, description="Text chunk size for splitting")
    CHUNK_OVERLAP: int = Field(default=30, description="overlap between chunks")

    # LLM setting
    LLM_TEMPERATURE: float = Field(default=0.3, description="LLM temperature")
    LLM_MAX_TOKENS: int = Field(default=10000, description="LLM max token output")

    # validating fields contain value
    @field_validator("CSV_FILE_PATH")
    def validate_csv_path(cls, v):
        """convert to absoulte path and check if file exists"""
        csv_path = Path(v)
        print(csv_path)
        if not csv_path.exists():
            raise ValueError(
                f" CSV file not found at {csv_path}"
                f"Please ensure the file exists or update CSV_FILE_PATH in .env"
            )
        return str(csv_path.resolve())

    @field_validator("QDRANT_API_KEY", "GEMINI_API_KEY")
    def validate_api_key(cls, v, field):
        """Ensures api keys are not empty"""
        if not v or v.strip() == "":
            raise ValueError(f"{field} is required but found empty")
        return v.strip()


settings = Settings()
