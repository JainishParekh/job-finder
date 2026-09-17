from workflow.graph import build_job_graph
from workflow.state import JobState


def test_job_analysis_workflow():

    graph = build_job_graph()

    state = JobState(
        company_name="Test Company",
        company_location="Berlin",
        job_title="Working Student Machine Learning",
        job_description="""
        We are looking for a working student
        with Python, FastAPI, machine learning
        and React experience.
        """,
    )

    result = graph.invoke(
        state.model_dump()
    )

    assert result["job_match"] is not None

    print("\nJOB MATCH:")
    print(
        result["job_match"]
    )