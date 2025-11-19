# Create text indexes for filterable fields
from qdrant_client import models

from qdrant import client, collection_name


def make_index(field_name_to_index):
    for field_name in field_name_to_index:
        if field_name =='publication_date':
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
