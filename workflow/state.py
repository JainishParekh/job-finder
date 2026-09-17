from typing import Optional
from pydantic import BaseModel, Field
from schemas.job_match import JobMatch
from schemas.candidate_profile import CandidateProfile

class JobState(BaseModel):

    # ========================================================
    # Job input
    # ========================================================

    job_url: str = ""
    company_name: str = ""
    company_location: str = ""
    job_title: str = ""
    job_description: str = ""
    
    # ========================================================
    # Candidate Source of Truth
    # ========================================================

    candidate_profile: Optional[CandidateProfile] = None

    # ========================================================
    # Candidate / retrieval
    # ========================================================

    candidate_context: str = ""

    # ========================================================
    # LLM analysis
    # ========================================================

    job_match: Optional[JobMatch] = None

    # ========================================================
    # Later stages
    # ========================================================

    tailored_resume: Optional[dict] = None
    cover_letter: Optional[str] = None

    # ========================================================
    # Workflow control
    # ========================================================

    errors: list[str] = Field(default_factory=list)
