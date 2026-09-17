from rag.candidate_profile import load_candidate_profile
from rag.ingest import build_documents


def test_build_candidate_documents():

    profile = load_candidate_profile()

    documents = build_documents(profile)

    assert documents
    assert len(documents) > 0


def test_documents_have_required_fields():

    profile = load_candidate_profile()

    documents = build_documents(profile)

    for document in documents:

        assert "id" in document
        assert "document" in document
        assert "metadata" in document

        assert document["id"]
        assert document["document"]
        assert isinstance(document["metadata"], dict)


def test_expected_document_types_exist():

    profile = load_candidate_profile()

    documents = build_documents(profile)

    types = {document["metadata"]["type"] for document in documents}

    assert "work" in types
    assert "work_highlight" in types
    assert "project" in types
    assert "project_highlight" in types
    assert "conference" in types
    assert "achievement" in types
    assert "skills" in types
    assert "languages" in types
