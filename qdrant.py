import os
import uuid

from qdrant_client import QdrantClient, models

from config import settings

client = QdrantClient(
    location=settings.QDRANT_LOCATION,
    api_key=settings.QDRANT_API_KEY,
)

# Define the collection name
collection_name = settings.COLLECTION_NAME

# Create our collection with both sparse (bm25) and dense vectors only if it doesn't exist
if not client.collection_exists(collection_name):
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
    print(f"Created collection: {collection_name}")
else:
    print(f"Collection {collection_name} already exists, using existing collection")


def make_embedding_save_to_db(chunks_with_metadata, batch_size=50):
    """
    Upload chunks in batches to avoid payload size limits
    """
    total_chunks = len(chunks_with_metadata)

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
                            model="sentence-transformers/all-MiniLM-L6-v2",
                        ),
                        "sparse": models.Document(
                            text=chunk["text"],
                            model="Qdrant/bm25",
                        ),
                    },
                    payload={"text": chunk["text"], **chunk["metadata"]},
                )
                for chunk in batch
            ],
        )

        print(
            f"Uploaded batch {i // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size} ({len(batch)} chunks)"
        )
