from schemas.job_match import JobMatch
from pathlib import Path
from schemas.candidate_profile import CandidateProfile
from schemas.cover_letter import CoverLetter
from llm.client import get_llm_client

llm = get_llm_client()
RULES_MD_PATH = Path(__file__).parent.parent / "data" / "rules.md"


def _load_rules() -> str:
    if not RULES_MD_PATH.exists():
        raise FileNotFoundError(f"Rules file not found: {RULES_MD_PATH}")
    return RULES_MD_PATH.read_text(encoding="utf-8")


def generate_cover_letter(
    candidate_profile: CandidateProfile,
    candidate_context: str,
    job_match: JobMatch,
    job_description: str,
    company_research: str,
    company_name: str,
) -> CoverLetter:

    rules = _load_rules()

    system_prompt = f"""You are a career expert tailoring application materials for a candidate applying for jobs in Germany.
    Using ONLY candidate facts, align the experience closely with the Job Description.
    Do NOT invent claims or experience.

        Rules:
        {rules}

        Candidate Profile:
        {candidate_profile.model_dump_json()}
    """

    user_prompt = f"""Company: {company_name}

        Job Description:
        {job_description}

        Job Match Notes:
        {job_match.model_dump_json()}

        Company Research:
        {company_research}

        Candidate profile context which is more relevant as pe job description:
        {candidate_context}

    """

    return llm.structured_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=CoverLetter,
        temperature=0.5,
    )
