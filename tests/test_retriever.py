from rag.retriever import (
    retrieve_candidate_documents,
    get_relevant_candidate_context,
)


def test_retrieve_candidate_documents():

    job_description = """
    Working student position in AI and software engineering.

    Requirements:
    Python
    FastAPI
    React
    machine learning
    """

    results = retrieve_candidate_documents(
        job_description,
        top_k=5,
    )

    assert results is not None

    assert "documents" in results
    assert "metadatas" in results
    assert "distances" in results

    documents = results["documents"][0]

    assert len(documents) > 0


def test_retrieved_documents_have_metadata():

    job_description = """
    Software engineering working student.
    React, TypeScript, Node.js and backend development.
    """

    results = retrieve_candidate_documents(
        job_description,
        top_k=5,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    assert len(documents) == len(metadatas)

    for metadata in metadatas:

        assert isinstance(metadata, dict)
        assert "type" in metadata


def test_get_relevant_candidate_context():

    job_description = """
    Python machine learning AI working student.
    """

    context = get_relevant_candidate_context(
        job_description,
        top_k=5,
    )

    assert isinstance(context, str)
    assert len(context) > 0

    assert "CANDIDATE EVIDENCE" in context
