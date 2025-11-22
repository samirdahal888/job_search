"""Data ingestion configuration"""

from pathlib import Path

from pydantic import Field, field_validator

from common.base_config import BaseConfig


class DataIngestionConfig(BaseConfig):
    """Configuration for data ingestion module - Data processing specific settings"""

    # CSV file path
    CSV_FILE_PATH: str = Field(
        default="lf_job.csv",
        description="Path to the CSV file (relative to artifacts folder)",
    )

    # Text chunking settings
    CHUNK_SIZE: int = Field(default=300, description="Text chunk size for splitting")
    CHUNK_OVERLAP: int = Field(default=30, description="Overlap between chunks")

    # validating fields contain value
    @field_validator("CSV_FILE_PATH")
    @classmethod
    def validate_csv_path(cls, v):
        """convert to absolute path and check if file exists"""
        # Look for CSV in data_ingestion/artifacts/
        csv_path = Path(__file__).parent / "artifacts" / Path(v).name
        if not csv_path.exists():
            raise ValueError(
                f"CSV file not found at {csv_path}. "
                f"Please ensure the file exists or update CSV_FILE_PATH in .env"
            )
        return str(csv_path.resolve())
