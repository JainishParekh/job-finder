from pathlib import Path
import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

RESUME_PATH = DATA_DIR / "resume.md"

EMBEDDINGS_CACHE_PATH = DATA_DIR / "embeddings_cache.npy"

CHUNKS_CACHE_PATH = DATA_DIR / "chunks_cache.json"


# --------------------------------------------------
# Embedding model
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


def parse_markdown_to_chunks(
    filepath: Path,
) -> list[dict]:
    """
    Read Markdown and split it into semantic chunks.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_blocks = re.split(r"\n---\n|\n\n", content)

    chunks = []

    for i, block in enumerate(raw_blocks):

        clean_block = block.strip()

        if len(clean_block) <= 20:
            continue

        chunks.append(
            {
                "id": f"md_chunk_{i}",
                "content": clean_block,
            }
        )

    return chunks


def generate_embeddings():
    """
    Read resume.md, create chunks,
    generate embeddings and save them locally.
    """

    if not RESUME_PATH.exists():
        raise FileNotFoundError(f"Resume not found: {RESUME_PATH}")

    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print(f"Reading resume: {RESUME_PATH}")

    chunks = parse_markdown_to_chunks(RESUME_PATH)

    print(f"Generating embeddings for " f"{len(chunks)} chunks...")

    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    np.save(EMBEDDINGS_CACHE_PATH, embeddings)

    with open(CHUNKS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print("✅ Embeddings generated.")

    print(f"Embeddings: {EMBEDDINGS_CACHE_PATH}")

    print(f"Chunks: {CHUNKS_CACHE_PATH}")


if __name__ == "__main__":
    generate_embeddings()
