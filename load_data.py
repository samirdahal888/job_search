import pandas as pd


def load_data():
    df = pd.read_csv(r"/home/samir-dahal/leapfrog_job_search/lf_job.csv")
    return df
