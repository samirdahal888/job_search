"""Qdrant-specific configuration"""

from pydantic import Field

from common.config.base_config import BaseConfig
from pydantic import field_validator


class QdrantConfig(BaseConfig):
    """Qdrant vector database configuration"""

    # sparse model and dense models
    SPARSE_MODEL: str = Field(
        default="Qdrant/bm25", description="Model for sparse search"
    )
    DENSE_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model for dense search",
    )
    QDRANT_API_KEY: str = Field(..., description="Qdrant cloud API key")
    QDRANT_LOCATION: str = Field(..., description="Qdrant cloud location/URL")

    COLLECTION_NAME: str = Field(
        default="hybrid_search", description="Qdrant collection name"
    )
    @field_validator("QDRANT_API_KEY")
    @classmethod
    def validate_api_key(cls, v):
        """Ensures API key is not empty"""
        if not v or not v.strip():
            raise ValueError("GEMINI_API_KEY is required but found empty")
        return v.strip()
