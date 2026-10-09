import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "chroma_db"
COLLECTION_NAME = "aau_documents"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to existing ChromaDB
client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def search_documents(question, top_k=3):

    # Convert student question into an embedding
    question_embedding = model.encode(question).tolist()

    # Search ChromaDB for similar document chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        matches.append({
            "text": text,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": distance
        })

    return matches


if __name__ == "__main__":

    question = "When does the first semester start?"

    print(f"\nQuestion: {question}")

    results = search_documents(question)

    for index, result in enumerate(results, start=1):

        print(f"\n--- Result {index} ---")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Text:\n{result['text']}")