
def unique_result_output(result):
        unique_jobs = {}
        for point in result:
            job_id = point.payload.get('chunk_id')

            if  job_id:
                if job_id not in unique_jobs or point.score >unique_jobs[job_id].score:
                    unique_jobs[job_id] =point
        return unique_jobs



def sorted_unique_result_with_hig_score(unique_jobs):
    sorted_high_score_job = sorted(
         unique_jobs.values(), 
         key=lambda x: x.score,
         reverse=True)
    
    return sorted_high_score_job
    
    

    
