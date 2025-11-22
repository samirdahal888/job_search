"""Vector search operations"""

from datetime import datetime

from qdrant_client import models

from common.logger import get_logger
from common.qdrant_config import QdrantConfig
from data_ingestion.qdrant_client import client, collection_name

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
    conditions = []
    logger.debug(f"Building filter condition from :{filter_dict}")

    for key, value in filter_dict.items():
        if value:
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
                logger.debug(f"Adding filter: {key} ={value}")
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchPhrase(phrase=value),
                    )
                )
    if conditions:
        logger.info(f"Created {len(conditions)} filter condition")
    else:
        logger.info("No filters applied to search")
    return models.Filter(must=conditions)


def search(query: str, filters=None, limit=5) -> list[models.ScoredPoint]:
    """Perform hybrid search on vector database

    Args:
        query: Search query string
        filters: Optional filter object
        limit: Maximum number of results

    Returns:
        List of scored points from search
    """
    logger.info(f"searching for:{query} ,limit {limit} ")
    start_time = datetime.now()
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
    elapsed = (datetime.now() - start_time).total_seconds()
    results_count = len(response.points)

    logger.info(f"Found {results_count} results in {elapsed:.2f}s")
    return response.points
