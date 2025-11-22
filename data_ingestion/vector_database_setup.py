"""Vector database setup script"""

from common.logger import get_logger
from common.utils import remove_html_tags
from data_ingestion.config import DataIngestionConfig
from data_ingestion.create_chunks import create_chunks
from data_ingestion.ingestion import load_data
from data_ingestion.qdrant_client import (
    create_field_indexes,
    upload_chunks_to_vector_db,
)

config = DataIngestionConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)


def setup_vector_database():
    """Main function to setup vector database with job data"""
    logger.info("Starting database setup process")
    logger.info("Loading data from the CSV")
    data = load_data()
    logger.info(f"Loaded {len(data)} job records")

    logger.info("Cleaning HTML from job description")
    data["Job Description"] = data["Job Description"].apply(remove_html_tags)
    logger.info("HTML cleaning completed")

    all_chunks = []

    logger.info("Creating chunks from job description")
    for id, row in data.iterrows():
        metadata = {
            "id": row.get("ID"),
            "category": row.get("Job Category", ""),
            "location": row.get("Job Location", ""),
            "company": row.get("Company Name", ""),
            "Level": row.get("Job Level", ""),
            "publication_date": row.get("Publication Date", ""),
        }

        chunks = create_chunks(
            job_title=row.get("Job Title"),
            description=row["Job Description"],
            metadata=metadata,
        )

        all_chunks.extend(chunks)

    logger.info(f"Created {len(all_chunks)} chunks from {len(data)} data")

    logger.info("Uploading chunks to Qdrant")
    upload_chunks_to_vector_db(all_chunks)

    logger.info("creating field indexes")
    field_names = ["category", "location", "company", "Level", "publication_date"]
    create_field_indexes(field_names)
    logger.info(f"Created index for fields: {field_names}")

    logger.info("Database setup completed successfully")


if __name__ == "__main__":
    setup_vector_database()
