from typing import Literal
from workflow.constants import Constants
from workflow.state import JobState

def verify_and_filter_analyzed_job(state: JobState) -> Literal[Constants.SUCCESS, Constants.FAILURE]:
    
    if not state.job_match:
        return Constants.FAILURE
    
    if state.job_match.match_score < 50:
        return Constants.FAILURE
    
    return Constants.SUCCESS