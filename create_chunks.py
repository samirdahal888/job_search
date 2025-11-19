from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(job_title, description, metadata):
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=30, length_function=lambda text: len(text.split())
    )
    text_chunks = text_splitter.split_text(description)
    for id, chunk_text in enumerate(text_chunks):
        chunks.append(
            {
                "text": f" Job Title: {job_title}.{chunk_text.strip()}",
                "metadata": {
                    "chunk_id": metadata.get("id"),
                    "job_title": job_title,
                    "category": metadata.get("category", ""),
                    "location": metadata.get("location", ""),
                    "company": metadata.get("company", ""),
                    "Level": metadata.get("Level", ""),
                    "publication_date": metadata.get("publication_date"),
                },
            }
        )
    return chunks
