#   database setup
from datetime import datetime

from clean_data import clean_html
from create_chunks import create_chunks
from index import make_index
from load_data import load_data
from qdrant import make_embedding_save_to_db
from logger import get_logger
logger = get_logger(__name__)


logger.info("Starting database setup process")
logger.info("Loading data from the CSV")
data = load_data()
logger.info(f"Loaded{len(data)} job records")
logger.info("Cleaning HTML from job description")
data["Job Description"] = data["Job Description"].apply(clean_html)
logger.info('HTML cleaning completed')
all_chunks = []

logger.info("Creating chunks from job description")
for id, row in data.iterrows():
    metadata = {
        "id": row.get("ID"),
        "category": row.get("Job Category", ""),
        "location": row.get("Job Location", ""),
        "company": row.get("Company Name", ""),
        "Level": row.get("Job Level", ""),
        "publication_date": row.get(
            "Publication Date", ""
        ),  
    }

    chunks = create_chunks(
        job_title=row.get("Job Title"),
        description=row["Job Description"],
        metadata=metadata,
    )

    all_chunks.extend(chunks)

logger.info(f"Created {len(all_chunks)} chunks from {len(data)} data")

logger.info('Uploading chunks to Qdrant')
make_embedding_save_to_db(all_chunks)

logger.info("creating field indexes")
field_to_index = ["category", "location", "company", "Level","publication_date"]
make_index(field_to_index)
logger.info(f"Created index for fields: {field_to_index}")

logger.info("Database setup completed successfully")