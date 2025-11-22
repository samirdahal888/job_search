"""Vector search operations"""

from datetime import datetime

from qdrant_client import models

from common.logger import get_logger
from common.qdrant_config import QdrantConfig
from data_ingestion.qdrant_client import client, collection_name
from search.exceptions import VectorDatabaseError

config = QdrantConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)


def create_filter_object(filter_dict):
    """Create Qdrant filter object from filter dictionary

    Args:
        filter_dict: Dictionary of filter conditions

    Returns:
        Qdrant Filter object
    """
    # Principle 3: Validate inputs to prevent exceptions
    if not filter_dict:
        logger.info("No filters provided, returning empty filter")
        return models.Filter(must=[])

    if not isinstance(filter_dict, dict):
        logger.warning(f"Invalid filter_dict type: {type(filter_dict)}, expected dict")
        return models.Filter(must=[])

    conditions = []
    logger.debug(f"Building filter condition from: {filter_dict}")

    for key, value in filter_dict.items():
        if value:
            try:
                # Handle datetime range for publication_date
                if key == "date_range" and isinstance(value, dict):
                    conditions.append(
                        models.FieldCondition(
                            key="publication_date",
                            range=models.DatetimeRange(
                                gt=value.get("gt"),
                                gte=value.get("gte"),
                                lt=value.get("lt"),
                                lte=value.get("lte"),
                            ),
                        )
                    )
                else:
                    # Regular field matching for other fields
                    logger.debug(f"Adding filter: {key} = {value}")
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchPhrase(phrase=value),
                        )
                    )
            except Exception as e:
                # Principle 2: Don't fail entire operation for one bad filter
                logger.warning(f"Failed to add filter {key}={value}: {e}")
                # Continue with other filters

    if conditions:
        logger.info(f"Created {len(conditions)} filter condition(s)")
    else:
        logger.info("No valid filters applied to search")

    return models.Filter(must=conditions)


def search(query: str, filters=None, limit=5) -> list[models.ScoredPoint]:
    """Perform hybrid search on vector database

    Args:
        query: Search query string
        filters: Optional filter object
        limit: Maximum number of results

    Returns:
        List of scored points from search

    Raises:
        VectorDatabaseError: If search operation fails
    """
    # Principle 3: Validate inputs to prevent exceptions
    if not query or not query.strip():
        logger.warning("Empty query provided to vector search")
        return []

    if limit <= 0:
        logger.warning(f"Invalid limit {limit}, using default of 5")
        limit = 5

    logger.info(f"Searching for: '{query}', limit: {limit}")
    start_time = datetime.now()

    # Principle 2: Use specific exception handling for Qdrant operations
    try:
        response = client.query_points(
            collection_name=collection_name,
            prefetch=[
                models.Prefetch(
                    query=models.Document(text=query, model=config.SPARSE_MODEL),
                    using="sparse",
                    limit=20,
                ),
                models.Prefetch(
                    query=models.Document(text=query, model=config.DENSE_MODEL),
                    using="dense",
                    limit=20,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            query_filter=filters,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Vector database query failed: {e}")
        raise VectorDatabaseError(f"Search operation failed: {str(e)}") from e

    elapsed = (datetime.now() - start_time).total_seconds()

    # Principle 3: Validate response structure
    if not response or not hasattr(response, "points"):
        logger.error("Invalid response from Qdrant: missing 'points' attribute")
        raise VectorDatabaseError("Vector database returned invalid response")

    results_count = len(response.points)
    logger.info(f"Found {results_count} result(s) in {elapsed:.2f}s")

    return response.points
