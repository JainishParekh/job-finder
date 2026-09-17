from rag.chroma import get_candidate_collection

# ============================================================
# Configuration
# ============================================================

DEFAULT_TOP_K = 8


# ============================================================
# Candidate Retrieval
# ============================================================


def retrieve_candidate_documents(
    job_description: str,
    top_k: int = DEFAULT_TOP_K,
):
    """
    Retrieve candidate evidence relevant to a job description.

    Returns Chroma results containing:
        - documents
        - metadatas
        - distances
    """

    collection = get_candidate_collection()

    results = collection.query(
        query_texts=[job_description],
        n_results=top_k,
    )

    return results


# ============================================================
# Formatted Retrieval
# ============================================================


def get_relevant_candidate_context(
    job_description: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:

    results = retrieve_candidate_documents(
        job_description,
        top_k=top_k,
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        return ""

    return "\n\n".join(
        ["--- CANDIDATE EVIDENCE ---\n" + document for document in documents]
    )


# ============================================================
# Debug / Manual Test
# ============================================================


if __name__ == "__main__":

    sample_job = """
    We are looking for a working student
    with Python, FastAPI, machine learning
    and React experience.
    """

    results = retrieve_candidate_documents(
        sample_job,
        top_k=8,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for index, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):

        print("\n" + "=" * 70)
        print(f"Result {index}")
        print(f"Distance: {distance:.4f}")
        print(f"Metadata: {metadata}")
        print(document)
