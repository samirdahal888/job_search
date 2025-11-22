from pydantic import BaseModel, Field

from api_config import api_config


class QueryRequest(BaseModel):
    """Request model for job search query"""

    query: str = Field(max_length=120, min_length=2)
    top: int = Field(
        default=api_config.DEFAULT_QUERY_RESULT, ge=1, le=api_config.MAX_QUERY_RESULT
    )
