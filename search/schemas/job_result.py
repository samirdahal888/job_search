from typing import Optional
from pydantic import BaseModel

class JobResult(BaseModel):
    """Individual job result model"""

    rank: int
    score: float
    job_title: str
    company: str
    category: str
    location: Optional[str] = None
    job_level: str
    job_id: str
    publication_date: Optional[str] = None
    description_snippet: Optional[str] = None