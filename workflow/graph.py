from langgraph.graph import StateGraph, START, END
from workflow.constants import Constants
from workflow.state import JobState
from workflow.nodes.analyze_job import analyze_job_node
from workflow.nodes.retrieve_context import retrieve_candidate_evidence
from workflow.nodes.tailor_resume import generate_tailored_resume
from workflow.nodes.generate_cover_letter import generate_cover_letter
from workflow.nodes.verify_output import verify_and_filter_analyzed_job
from workflow.nodes.research_company import research_company


def build_job_graph():

    builder = StateGraph(JobState)

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    builder.add_node("analyze_job", analyze_job_node)
    builder.add_node("retrieve_context", retrieve_candidate_evidence)
    builder.add_node("generate_cover_letter", generate_cover_letter)
    builder.add_node("generate_tailored_resume", generate_tailored_resume)
    builder.add_node("research_company", research_company)

    # --------------------------------------------------------
    # Flow
    # --------------------------------------------------------

    builder.add_edge(START, "retrieve_context")
    builder.add_edge("retrieve_context", "analyze_job")
    builder.add_conditional_edges(
        "analyze_job",
        verify_and_filter_analyzed_job,
        {Constants.SUCCESS: "research_company", Constants.FAILURE: END},
    )
    builder.add_edge("research_company", "generate_tailored_resume")
    builder.add_edge("research_company", "generate_cover_letter")
    builder.add_edge("generate_tailored_resume", END)
    builder.add_edge("generate_cover_letter", END)

    return builder.compile()


if __name__ == "__main__":

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

    result = graph.invoke(state.model_dump())

    print(result)
