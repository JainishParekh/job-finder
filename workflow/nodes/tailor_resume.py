from workflow.state import JobState
from schemas.tailored_resume import TailoredResume
from llm.resume_generator import generate_resume


def generate_tailored_resume(state: JobState):

    if not state.candidate_profile:
        state.errors.append("CANDIDATE_PROFILE_MISSING")
        return state

    if not state.job_match:
        state.errors.append("JOB_MATCH_MISSING")
        return state

    if not state.company_research:
        state.errors.append("COMPANY_RESEARCH_MISSING")
        return state

    # Store in state
    response = generate_resume(
        state.candidate_profile,
        state.candidate_context,
        state.job_match,
        state.job_description,
        state.company_research,
    )
    
    state.tailored_resume = response.model_dump()

    return { "tailored_resume":  response.model_dump()}
