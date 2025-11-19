from qdrant_client import QdrantClient, models

from qdrant import client, collection_name


def apply_filter(filter_dict):
    conditions = []

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
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchPhrase(phrase=value),
                    )
                )
    print(f"\nThis are the filter conditions{conditions}")
    return models.Filter(must=conditions)


def search(query: str, filters=None, limit=5) -> list[models.ScoredPoint]:
    response = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=models.Document(text=query, model="Qdrant/bm25"),
                using="sparse",
                limit=20,
            ),
            models.Prefetch(
                query=models.Document(
                    text=query, model="sentence-transformers/all-MiniLM-L6-v2"
                ),
                using="dense",
                limit=20,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        query_filter=filters,
        limit=limit,
    )
    return response.points
