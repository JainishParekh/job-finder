from workflow.state import JobState
from typing import Literal
from llm.matcher import analyze_job_match
from workflow.constants import Constants


def analyze_job_node(state: JobState) -> JobState:

    if not state.job_description.strip():
        state.errors.append("Job description is empty.")
        return state
    
    if not state.candidate_context.strip():
        state.errors.append("Candidate context is empty.")
        return state
    
    if not state.candidate_profile:
        state.errors.append("Candidate profile is empty.")
        return state
    

    result = analyze_job_match(state.job_description, state.candidate_context, state.candidate_profile)

    if not result.get("success"):
        state.errors.append(result.get("reason", "JOB_MATCH_FAILED"))
        return state

    state.job_match = result["data"]

    return state
