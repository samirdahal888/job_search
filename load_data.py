import pandas as pd

from config import settings


def load_data():
    df = pd.read_csv(settings.CSV_FILE_PATH)
    return df
