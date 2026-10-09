import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("data/processed/chunks.json")
DB_PATH = "chroma_db"
COLLECTION_NAME = "aau_documents"


def create_embeddings():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not chunks:
        print("No document chunks found.")
        return

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings...")
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    ).tolist()

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": chunk["source"],
                "page": chunk["page"]
            }
            for chunk in chunks
        ]
    )

    print("\nEmbeddings stored successfully!")
    print(f"Total chunks in database: {collection.count()}")


if __name__ == "__main__":
    create_embeddings()