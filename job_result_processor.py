def find_unique_results(result):
    unique_jobs = {}
    for point in result:
        job_id = point.payload.get("chunk_id")

        if job_id:
            if job_id not in unique_jobs or point.score > unique_jobs[job_id].score:
                unique_jobs[job_id] = point
    return unique_jobs


def sort_results_by_score(unique_jobs):
    sorted_jobs = sorted(unique_jobs.values(), key=lambda x: x.score, reverse=True)

    return sorted_jobs
