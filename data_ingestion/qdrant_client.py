"""Qdrant client initialization and vector database operations"""

import uuid

from qdrant_client import QdrantClient, models

from common.logger import get_logger
from common.qdrant_config import QdrantConfig

config = QdrantConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)

try:
    client = QdrantClient(
        location=config.QDRANT_LOCATION,
        api_key=config.QDRANT_API_KEY,
    )
    logger.info("Successfully connected to Qdrant")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    raise


collection_name = config.COLLECTION_NAME

if not client.collection_exists(collection_name):
    logger.info(f"Creating new collection:{collection_name}")
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": models.VectorParams(
                distance=models.Distance.COSINE,
                size=384,
            ),
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
        },
    )
    logger.info(f"Created collection : {collection_name}")
else:
    logger.info(f"Collection name already exist: {collection_name} using it .")


def upload_chunks_to_vector_db(chunks_with_metadata, batch_size=50):
    """
    Upload chunks in batches to avoid payload size limits

    Args:
        chunks_with_metadata: List of chunks with text and metadata
        batch_size: Number of chunks to upload per batch
    """
    total_chunks = len(chunks_with_metadata)
    logger.info(f"Starting upload of {total_chunks} chunks in batch of {batch_size}")

    for i in range(0, total_chunks, batch_size):
        batch = chunks_with_metadata[i : i + batch_size]

        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=uuid.uuid4().hex,
                    vector={
                        "dense": models.Document(
                            text=chunk["text"],
                            model=config.DENSE_MODEL,
                        ),
                        "sparse": models.Document(
                            text=chunk["text"],
                            model=config.SPARSE_MODEL,
                        ),
                    },
                    payload={"text": chunk["text"], **chunk["metadata"]},
                )
                for chunk in batch
            ],
        )

        logger.info(
            f"Uploaded batch {i // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size} ({len(batch)} chunks)"
        )
    logger.info(f"Successfully uploaded all {total_chunks} chunks to Qdrant")


def create_field_indexes(field_names):
    """Create text indexes for filterable fields

    Args:
        field_names: List of field names to index
    """
    for field_name in field_names:
        if field_name == "publication_date":
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=models.DatetimeIndexParams(
                    type=models.DatetimeIndexType.DATETIME,
                    is_principal=True,
                ),
            )
        else:
            # Create text index for other fields
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.WORD,
                    phrase_matching=True,
                    min_token_len=2,
                    max_token_len=10,
                    lowercase=True,
                ),
            )
