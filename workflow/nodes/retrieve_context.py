from workflow.state import JobState
from rag.retriever import get_relevant_candidate_context
from rag.candidate_profile import load_candidate_profile


def retrieve_candidate_evidence(
    state: JobState,
) -> JobState:

    candidate_context = get_relevant_candidate_context(state.job_description)

    if not candidate_context:
        state.errors = ["NO_CANDIDATE_CONTEXT"]
        return state

    state.candidate_profile = load_candidate_profile()
    state.candidate_context = candidate_context
    return state
