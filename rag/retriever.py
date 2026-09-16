from pathlib import Path
import json

import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

EMBEDDINGS_CACHE_PATH = (DATA_DIR / "embeddings_cache.npy")

CHUNKS_CACHE_PATH = (DATA_DIR / "chunks_cache.json")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

SIMILARITY_GATE_THRESHOLD = 0.25


# --------------------------------------------------
# Lazy-loaded objects
# --------------------------------------------------

_embedder = None
_resume_embeddings = None
_resume_chunks = None


def _ensure_loaded():

    global _embedder, _resume_embeddings, _resume_chunks

    if _embedder is None:

        print(f"Loading embedding model: {MODEL_NAME}")

        _embedder = SentenceTransformer(MODEL_NAME)

    if _resume_embeddings is None or _resume_chunks is None:

        if not EMBEDDINGS_CACHE_PATH.exists():

            raise RuntimeError(
                "Embedding cache missing. "
                "Run:\n\n"
                "python -m rag.embeddings")

        if not CHUNKS_CACHE_PATH.exists():

            raise RuntimeError(
                "Chunk cache missing. "
                "Run:\n\n"
                "python -m rag.embeddings"
            )

        _resume_embeddings = np.load(EMBEDDINGS_CACHE_PATH)

        with open(CHUNKS_CACHE_PATH, "r", encoding="utf-8") as f:
            _resume_chunks = json.load(f)


def get_relevant_chunks(
    job_description: str,
    top_k: int = 4,
) -> tuple[str, float]:

    """
    Retrieve the most relevant resume chunks for a given job description.

    Returns:
        relevant_experience
        max_similarity
    """

    _ensure_loaded()

    job_embedding = _embedder.encode(job_description, normalize_embeddings=True)

    similarities = np.dot(_resume_embeddings, job_embedding)

    top_indices = np.argsort(similarities)[::-1][:top_k]

    max_similarity = (
        float(similarities[top_indices[0]])
        if len(top_indices)
        else 0.0
    )

    chunks_text = "\n\n".join(
        (
            "--- RELEVANT EXPERIENCE ---\n"
            + _resume_chunks[i]["content"]
        )
        for i in top_indices
    )

    return (
        chunks_text,
        max_similarity,
    )


if __name__ == "__main__":

    sample_job = """
    We are looking for a working student
    with Python, FastAPI, machine learning
    and React experience.
    """

    chunks, score = get_relevant_chunks(
        sample_job
    )

    print(
        f"\nSimilarity: {score:.3f}\n"
    )

    print(chunks)