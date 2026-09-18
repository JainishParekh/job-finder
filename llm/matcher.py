from schemas.job_match import JobMatch
from schemas.candidate_profile import CandidateProfile
from llm.client import get_llm_client

llm = get_llm_client()


def analyze_job_match(
    job_description: str,
    candidate_context: str,
    candidate_profile: CandidateProfile,
) -> dict:
    system_prompt = f"""
You are an expert technical recruiter evaluating a candidate for a job in Germany.
Your task is to analyze the candidate against the provided job description.
You must:

- Evaluate the candidate's actual fit.
- Give a match score from 0 to 100.
- Explain the main reasons for the score.
- Identify relevant candidate experience.
- Identify relevant candidate projects.
- Identify relevant candidate skills.
- Identify important job requirements that are not supported by the candidate evidence.
- Create up to three tailored resume bullets.

IMPORTANT GROUNDING RULE:
You MUST use ONLY facts explicitly present in the Candidate Evidence.
Never invent experience, technologies, responsibilities, years of experience, or achievements.
If a requirement is not supported by the Candidate Evidence, put it in "missing_requirements".

Candidate most relevant information:
{candidate_context}

Complete source of truth:
{candidate_profile.model_dump_json()}
"""
    user_prompt = f"Job Description:\n{job_description}"

    try:
        result = llm.structured_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=JobMatch,
            temperature=0.1,
        )
        return {"success": True, "data": result.model_dump()}
    except RuntimeError as e:
        return {"success": False, "reason": "VALIDATION_FAILED", "error": str(e)}