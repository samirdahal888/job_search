#   database setup
from datetime import datetime

from clean_data import clean_html
from create_chunks import create_chunks
from index import make_index
from load_data import load_data
from qdrant import make_embedding_save_to_db

data = load_data()
data["Job Description"] = data["Job Description"].apply(clean_html)
all_chunks = []

for id, row in data.iterrows():
    metadata = {
        "id": row.get("ID"),
        "category": row.get("Job Category", ""),
        "location": row.get("Job Location", ""),
        "company": row.get("Company Name", ""),
        "Level": row.get("Job Level", ""),
        "publication_date": row.get(
            "Publication Date", ""
        ),  # Store as datetime object, not string
    }
    # print(metadata)

    chunks = create_chunks(
        job_title=row.get("Job Title"),
        description=row["Job Description"],
        metadata=metadata,
    )
    # print(chunks)
    # make_embedding_save_to_db(chunks)
    # make_index(["category", "location", "company", "Level","publication_date"])

    # break

    all_chunks.extend(chunks)

make_embedding_save_to_db(all_chunks)

# # making index for the necessary field to make field level search easier and faster
make_index(["category", "location", "company", "Level","publication_date"])

print("Data base setup completed ")
