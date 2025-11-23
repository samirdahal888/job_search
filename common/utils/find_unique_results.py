def find_unique_results(result: list) -> dict:
    """Find unique job results by chunk_id, keeping highest score

    Args:
        result: List of search results with score and payload

    Returns:
        Dictionary of unique jobs keyed by job_id
    """
    unique_jobs = {}
    for point in result:
        job_id = point.payload.get("chunk_id")

        if job_id:
            if job_id not in unique_jobs or point.score > unique_jobs[job_id].score:
                unique_jobs[job_id] = point
    return unique_jobs