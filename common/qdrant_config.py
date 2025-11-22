"""Qdrant-specific configuration"""

from pydantic import Field

from common.base_config import BaseConfig


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
