"""Data ingestion script for loading and processing job data"""

import pandas as pd

from data_ingestion.config import DataIngestionConfig

config = DataIngestionConfig()


def load_data():
    """Load job data from CSV file

    Returns:
        DataFrame: Loaded job data
    """
    df = pd.read_csv(config.CSV_FILE_PATH)
    return df
