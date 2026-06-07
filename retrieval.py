"""
retrieval.py — Embedding + vector store + retrieval for The Unofficial Guide.

Implements Milestone 4 per planning.md Retrieval Approach:
    Embedding model : all-MiniLM-L6-v2 (sentence-transformers, local, no API key)
    Vector store    : ChromaDB, persistent on disk at ./chroma_db
    Retrieval       : top-k = 4 (planning.md spec)

Pipeline stages (per planning.md architecture diagram):
    ... Chunking -> Embedding + Vector Store -> Retrieval ...

Each stored chunk keeps metadata {"source": <filename>, "chunk_index": <int>}
carried over from ingest.py, so retrieval results are attributable (Milestone 5).
"""

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import chunk_documents

# --- Spec values from planning.md (Retrieval Approach section) ---
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 6
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "brandeis_housing"


# ----------------------------------------------------------------------------- #
# EMBEDDING MODEL                                                                #
# ----------------------------------------------------------------------------- #
def get_embedder():
    """Load the local all-MiniLM-L6-v2 model. Downloads once, then cached."""
    return SentenceTransformer(EMBED_MODEL_NAME)


# ----------------------------------------------------------------------------- #
# BUILD / LOAD THE VECTOR STORE                                                  #
# ----------------------------------------------------------------------------- #
def build_index(directory_path="text_files", reset=True):
    """
    Run ingestion -> embed every chunk -> store in a persistent ChromaDB collection
    with source metadata. Returns (collection, embedder).

    reset=True drops any existing collection first, so re-running after a chunking
    change (e.g. you changed CHUNK_SIZE) rebuilds cleanly instead of mixing old
    and new embeddings.
    """
    chunks = chunk_documents(directory_path)
    embedder = get_embedder()

    # PersistentClient writes the DB to disk so you don't re-embed every run.
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet — fine

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # cosine distance: 0 = identical, higher = less similar
    )

    # Embed all chunk texts in one batch (faster than one call per chunk).
    texts = [c.page_content for c in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=[f"{c.metadata['source']}::{c.metadata['chunk_index']}" for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[c.metadata for c in chunks],
    )

    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}' at {CHROMA_DIR}")
    return collection, embedder


def load_index():
    """Open the already-built persistent collection (no re-embedding of chunks)."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    embedder = get_embedder()
    return collection, embedder


# ----------------------------------------------------------------------------- #
# RETRIEVAL                                                                      #
# ----------------------------------------------------------------------------- #
def retrieve_housing_context(query, collection, embedder, k=TOP_K):
    """
    Embed the query, search the collection, return the top-k chunks.

    Returns a list of dicts: {text, source, chunk_index, distance}.
    distance is cosine distance — lower is a closer match (per the spec's
    'scores above 0.6-0.7 indicate weak matches' guidance).
    """
    q_emb = embedder.encode([query]).tolist()
    res = collection.query(query_embeddings=q_emb, n_results=k)

    results = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        results.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        })
    return results


# ----------------------------------------------------------------------------- #
# RETRIEVAL TEST (Milestone 4: test >=3 evaluation queries, print chunks+scores) #
# ----------------------------------------------------------------------------- #
if __name__ == "__main__":
    collection, embedder = build_index()

    # 3 of the 5 evaluation-plan queries from planning.md
    test_queries = [
        "What is a forced triple and which building is it most common in?",
        "What do students advise about the roommate matching form?",
        "What happens if the freshman quads fill up due to high enrollment?",
    ]

    for q in test_queries:
        print("\n" + "=" * 72)
        print(f"QUERY: {q}")
        print("=" * 72)
        for r in retrieve_housing_context(q, collection, embedder):
            print(f"\n  distance={r['distance']:.3f}  source={r['source']}  chunk={r['chunk_index']}")
            print(f"  {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}")