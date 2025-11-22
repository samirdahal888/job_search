"""Utility functions for the application"""

from bs4 import BeautifulSoup


def remove_html_tags(description: str) -> str:
    """Remove HTML tags from text using BeautifulSoup

    Args:
        description: HTML text to clean

    Returns:
        Cleaned text without HTML tags
    """
    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text(separator=" ")
    return text


def find_unique_results(result):
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


def sort_results_by_score(unique_jobs):
    """Sort job results by score in descending order

    Args:
        unique_jobs: Dictionary of unique jobs

    Returns:
        List of jobs sorted by score (highest first)
    """
    sorted_jobs = sorted(unique_jobs.values(), key=lambda x: x.score, reverse=True)
    return sorted_jobs
