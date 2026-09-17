from workflow.state import JobState
from schemas.tailored_resume import TailoredResume


def generate_tailored_resume(state: JobState) -> JobState:

    if not state.candidate_profile:
        state.errors.append("CANDIDATE_PROFILE_MISSING")
        return state

    if not state.job_match:
        state.errors.append("JOB_MATCH_MISSING")
        return state

    # Build prompt here
    # Call LLM
    # Validate with TailoredResume
    # Store in state

    return state
