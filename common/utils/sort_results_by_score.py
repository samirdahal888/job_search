def sort_results_by_score(unique_jobs: dict) -> list:
    """Sort job results by score in descending order

    Args:
        unique_jobs: Dictionary of unique jobs

    Returns:
        List of jobs sorted by score (highest first)
    """
    sorted_jobs = sorted(unique_jobs.values(), key=lambda x: x.score, reverse=True)
    return sorted_jobs