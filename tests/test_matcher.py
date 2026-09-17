from llm.matcher import (
    analyze_job_match,
)


def test_analyze_job_match():

    job_description = """
    Working student position in AI and software engineering.

    Requirements:
    Python
    FastAPI
    React
    Machine Learning
    """

    result = analyze_job_match(job_description)

    assert result["success"] is True

    data = result["data"]

    assert 0 <= data["match_score"] <= 100

    assert isinstance(
        data["match_reasoning"],
        str,
    )

    assert isinstance(
        data["relevant_experience"],
        list,
    )

    assert isinstance(
        data["relevant_projects"],
        list,
    )

    assert isinstance(
        data["relevant_skills"],
        list,
    )

    assert isinstance(
        data["missing_requirements"],
        list,
    )

    assert isinstance(
        data["tailored_bullets"],
        list,
    )
