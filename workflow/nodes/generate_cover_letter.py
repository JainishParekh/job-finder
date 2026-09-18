from workflow.state import JobState
from llm.cover_letter_generator import (
    generate_cover_letter as call_generate_cover_letter,
)


def generate_cover_letter(state: JobState):
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
    response = call_generate_cover_letter(
        state.candidate_profile,
        state.candidate_context,
        state.job_match,
        state.job_description,
        state.company_research,
        state.company_name,
    )

    return {"cover_letter": response}
