from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up ChromaDB
client = chromadb.Client()
collection = client.create_collection("reddit_posts")

# Embed and store your chunks
for i, chunk in enumerate(your_chunks):
    embedding = model.encode(chunk).tolist()
    collection.add(
        documents=[chunk],
        embeddings=[embedding],
        metadatas=[{"source": "post1.txt"}],  # track where it came from
        ids=[str(i)]
    )

# Query it
def retrieve(query, k=5):
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    return results