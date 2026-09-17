from pathlib import Path

import chromadb

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)

# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHROMA_PATH = PROJECT_ROOT / "data" / "chroma"


# ============================================================
# Configuration
# ============================================================

COLLECTION_NAME = "candidate_profile"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================================
# Client
# ============================================================


def get_chroma_client():

    CHROMA_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(path=str(CHROMA_PATH))


# ============================================================
# Candidate Collection
# ============================================================


def get_candidate_collection():

    client = get_chroma_client()

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
        device="cpu",
        normalize_embeddings=True,
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        configuration={"hnsw": {"space": "cosine"}},
    )
