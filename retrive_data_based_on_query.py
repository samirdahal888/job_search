from qdrant_client import models

from config import settings
from qdrant import client, collection_name
from logger import get_logger
from datetime import datetime
logger = get_logger(__name__)


def apply_filter(filter_dict):
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
    logger.info(f"searching for:{query} ,limit {limit} ")
    start_time = datetime.now()
    response = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=models.Document(text=query, model=settings.SPARSE_MODEL),
                using="sparse",
                limit=20,
            ),
            models.Prefetch(
                query=models.Document(text=query, model=settings.DENSE_MODEL),
                using="dense",
                limit=20,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        query_filter=filters,
        limit=limit,
    )
    elapsed = (datetime.now()-start_time).total_seconds()
    results_count =len(response.points)

    logger.info(f"Found {results_count} results in {elapsed:.2f}s")
    return response.points
