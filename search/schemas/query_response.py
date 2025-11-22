from typing import List
from search.schemas.job_result import JobResult
from pydantic import BaseModel


class QueryResponse(BaseModel):
    """Response model for job search query"""

    success: bool
    query: str
    response: str
    jobs: List[JobResult]
    timestamp: str
