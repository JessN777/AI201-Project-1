from sentence_transformers import SentenceTransformer
import chromadb
import os
import glob

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Persistent client so embeddings survive between runs
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("reddit_posts")


def load_and_embed_documents(docs_dir="."):
    """Read all .txt files in docs_dir and embed them into ChromaDB.
    Already-embedded files are skipped to avoid duplicates."""
    txt_files = glob.glob(os.path.join(docs_dir, "*.txt"))
    if not txt_files:
        print("No .txt files found.")
        return

    existing_ids = set(collection.get()["ids"])

    added = 0
    for filepath in txt_files:
        doc_id = os.path.basename(filepath)
        if doc_id in existing_ids:
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        embedding = model.encode(content).tolist()
        collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[{"source": doc_id}],
            ids=[doc_id]
        )
        added += 1

    print(f"Embedded {added} new document(s). Total in DB: {collection.count()}")


def retrieve(query, k=5):
    """Return the top-k most relevant chunks for a query."""
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count())
    )
    return results
