from pathlib import Path
from schemas.job_match import JobMatch
from schemas.candidate_profile import CandidateProfile
from schemas.tailored_resume import TailoredResume
from llm.client import get_llm_client

llm = get_llm_client()
RULES_MD_PATH = Path(__file__).parent.parent / "data" / "rules.md"


def _load_rules() -> str:
    if not RULES_MD_PATH.exists():
        raise FileNotFoundError(f"Rules file not found: {RULES_MD_PATH}")
    return RULES_MD_PATH.read_text(encoding="utf-8")


def generate_resume(
    candidate_profile: CandidateProfile,
    candidate_context: str,
    job_match: JobMatch,
    job_description: str,
    company_research: str,
) -> TailoredResume:
    rules = _load_rules()

    system_prompt = f"""You are a career expert tailoring resumes for candidates applying to jobs in Germany.

Rules:
{rules}

Constraints:
- Use ONLY facts present in the candidate profile. Never invent experience, skills, projects, or achievements.
- You MAY reorder, select, and rephrase existing bullets/skills to emphasize relevance.
- Use company research to align terminology only where genuinely backed by real candidate facts.
- Every list needs at least the minimum items described in its schema field, drawn only from real candidate data.

Candidate Profile:
{candidate_profile.model_dump_json()}
"""

    user_prompt = f"""Job Description:
{job_description}

Job Match Notes:
{job_match.model_dump_json()}

Company Research:
{company_research}

Job relevant candidate profile context:
{candidate_context}
"""

    return llm.structured_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=TailoredResume,
        temperature=0.4,
    )
