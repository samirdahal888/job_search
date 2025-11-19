from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from llm_response import LLM_response
from query_to_semantic_and_filter import convert_query_to_semantic_and_filter
from remove_duplicate_from_result import (
    sorted_unique_result_with_hig_score,
    unique_result_output,
)
from retrive_data_based_on_query import apply_filter, search

app = FastAPI(
    title="RAG Application for Job search",
    description="Intelligent job search using Retrieval-Augmented Generation",
    version="0.1",
    redoc_url="/redocs",
)


class QueryRequest(BaseModel):
    query: str
    top: int = Field(default=3)


class JobResult(BaseModel):
    rank: int
    Score: float
    job_title: str
    company: str
    category: str
    location: str
    job_level: str
    job_id: str
    Publication_Date: Optional[str] = None
    Description_snippet: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for job search query"""

    success: bool
    query: str
    response: str
    jobs: List[JobResult]
    timestamp: str


@app.get("/", tags=["Home"])
def home():
    return {
        "message": "LF Jobs RAG API",
        "version": 0.1,
        "description": "Intelligent job search using Retrieval-Augmented Generation",
        "endpoints": {
            "POST /api/query": "Search for jobs with natural language",
        },
    }


@app.post("/api/query", response_model=QueryResponse, tags=["Query"])
def job_query(request: QueryRequest):
    data = convert_query_to_semantic_and_filter(request.query)
    semantic = None
    filter = None

    for k, v in data.items():
        if k == "semantic_query":
            semantic = v
        elif k == "filters":
            filter = v

    print(f"\nThis is the semantic part ===={semantic}")
    print(f"\nThis is the filter part ===={filter}")

    filtered_value = apply_filter(filter)
    results = search(semantic, filtered_value, limit=request.top)

    unique_outputs = unique_result_output(results)
    unique_results = sorted_unique_result_with_hig_score(unique_outputs)
    response_from_llm = LLM_response(unique_results, request.query)

    job_result = []
    for i, point in enumerate(unique_results, 1):
        text = point.payload.get("text", "")
        snippet = text[:300] + "..." if len(text) > 300 else text

        job_result.append(
            JobResult(
                rank=i,
                Score=point.score,
                job_title=point.payload.get("job_title", "N/A"),
                company=point.payload.get("company", "N/A"),
                category=point.payload.get("category", "N/A"),
                location=point.payload.get("location", "N/A"),
                job_level=point.payload.get("Level", "N/A"),
                job_id=point.payload.get("chunk_id", "N/A"),
                Publication_Date=point.payload.get("publication_date"),
                Description_snippet=snippet,
            )
        )

    return QueryResponse(
        success=True,
        query=request.query,
        response=response_from_llm,
        jobs=job_result,
        timestamp=datetime.now().isoformat(),
    )
