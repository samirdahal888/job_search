"""Qdrant client initialization and vector database operations"""

import uuid

from qdrant_client import QdrantClient, models

from common.config.qdrant_config import QdrantConfig
from common.logger import get_logger


class QdrantClientManager:
    """Manager class for Qdrant client and vector database operations"""

    def __init__(self):
        """Initialize Qdrant client and ensure collection exists"""
        self.config = QdrantConfig()
        self.logger = get_logger(__name__)
        self.collection_name = self.config.COLLECTION_NAME

        # Initialize client
        try:
            self.client = QdrantClient(
                location=self.config.QDRANT_LOCATION,
                api_key=self.config.QDRANT_API_KEY,
            )
            self.logger.info("Successfully connected to Qdrant")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant: {e}")
            raise

        # Ensure collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist"""
        if not self.client.collection_exists(self.collection_name):
            self.logger.info(f"Creating new collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
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
            self.logger.info(f"Created collection: {self.collection_name}")
        else:
            self.logger.info(
                f"Collection name already exist: {self.collection_name} using it."
            )

    def upload_chunks_to_vector_db(
        self, chunks_with_metadata: list, batch_size: int = 50
    ) -> None:
        """
        Upload chunks in batches to avoid payload size limits

        Args:
            chunks_with_metadata: List of chunks with text and metadata
            batch_size: Number of chunks to upload per batch
        """
        total_chunks = len(chunks_with_metadata)
        self.logger.info(
            f"Starting upload of {total_chunks} chunks in batch of {batch_size}"
        )

        for i in range(0, total_chunks, batch_size):
            batch = chunks_with_metadata[i : i + batch_size]

            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=uuid.uuid4().hex,
                        vector={
                            "dense": models.Document(
                                text=chunk["text"],
                                model=self.config.DENSE_MODEL,
                            ),
                            "sparse": models.Document(
                                text=chunk["text"],
                                model=self.config.SPARSE_MODEL,
                            ),
                        },
                        payload={"text": chunk["text"], **chunk["metadata"]},
                    )
                    for chunk in batch
                ],
            )

            self.logger.info(
                f"Uploaded batch {i // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size} ({len(batch)} chunks)"
            )
        self.logger.info(f"Successfully uploaded all {total_chunks} chunks to Qdrant")

    def create_field_indexes(self, field_names: list) -> None:
        """Create text indexes for filterable fields

        Args:
            field_names: List of field names to index
        """
        for field_name in field_names:
            if field_name == "publication_date":
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=models.DatetimeIndexParams(
                        type=models.DatetimeIndexType.DATETIME,
                        is_principal=True,
                    ),
                )
            else:
                # Create text index for other fields
                self.client.create_payload_index(
                    collection_name=self.collection_name,
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


_qdrant_manager = QdrantClientManager()
client = _qdrant_manager.client
collection_name = _qdrant_manager.collection_name
upload_chunks_to_vector_db = _qdrant_manager.upload_chunks_to_vector_db
create_field_indexes = _qdrant_manager.create_field_indexes
