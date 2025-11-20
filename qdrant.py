import uuid

from qdrant_client import QdrantClient, models

from config import settings
from logger import get_logger

logger = get_logger(__name__)

try:
    client = QdrantClient(
        location=settings.QDRANT_LOCATION,
        api_key=settings.QDRANT_API_KEY,
    )
    logger.info("Successfully connected to Qdrant")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    raise


collection_name = settings.COLLECTION_NAME

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


def make_embedding_save_to_db(chunks_with_metadata, batch_size=50):
    """
    Upload chunks in batches to avoid payload size limits
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
                            model=settings.DENSE_MODEL,
                        ),
                        "sparse": models.Document(
                            text=chunk["text"],
                            model=settings.SPARSE_MODEL,
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
