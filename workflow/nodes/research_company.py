from workflow.state import JobState
from llm.company_research import research_company as call_research_company


def research_company(state: JobState):

    # check for required values
    if not state.company_name or not state.job_title or not state.job_description:
        state.errors = ["All the required values are not present in the state."]
        return state

    # call llm fo doing research
    state.company_research = call_research_company(
        company_name=state.company_name,
        job_title=state.job_title,
        job_description=state.job_description,
    )
    return state