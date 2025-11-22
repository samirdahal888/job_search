"""Create text chunks from job descriptions"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from data_ingestion.config import DataIngestionConfig

config = DataIngestionConfig()


def create_chunks(job_title, description, metadata):
    """Split job description into chunks with metadata

    Args:
        job_title: Title of the job
        description: Job description text
        metadata: Additional job metadata

    Returns:
        List of chunks with text and metadata
    """
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=lambda text: len(text.split()),
    )
    text_chunks = text_splitter.split_text(description)
    for id, chunk_text in enumerate(text_chunks):
        chunks.append(
            {
                "text": f" Job Title: {job_title}.{chunk_text.strip()}",
                "metadata": {
                    "chunk_id": metadata.get("id"),
                    "job_title": job_title,
                    "category": metadata.get("category", ""),
                    "location": metadata.get("location", ""),
                    "company": metadata.get("company", ""),
                    "Level": metadata.get("Level", ""),
                    "publication_date": metadata.get("publication_date"),
                },
            }
        )
    return chunks
