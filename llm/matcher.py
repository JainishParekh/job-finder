import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from schemas.job_match import JobMatch
from schemas.candidate_profile import CandidateProfile

# ============================================================
# Configuration
# ============================================================
GROQ_MODEL = "openai/gpt-oss-120b"
MAX_RETRIES = 3
RETRIEVAL_TOP_K = 8

# ============================================================
# Groq Client Initialization
# ============================================================
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ============================================================
# Main Function
# ============================================================
def analyze_job_match(
    job_description: str,
    candidate_context: str,
    candidate_profile: CandidateProfile,
    max_retries: int = MAX_RETRIES,
) -> dict:
    """
    Analyze how well the candidate matches a job description.

    1. Sends the job description, complete source of truth and retrieved evidence to the LLM.
    2. Validates the structured LLM response with Pydantic.
    """

    # --------------------------------------------------------
    # 1. System Prompt
    # --------------------------------------------------------
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
Never:
- invent experience
- invent technologies
- invent responsibilities
- invent years of experience
- invent achievements
- exaggerate responsibilities
- claim professional experience that is not provided
- claim fluent German unless explicitly stated

If a requirement is not supported by the Candidate Evidence, put it in "missing_requirements".
Do not assume that a technology is known just because it is similar to another technology.
Tailored resume bullets must also be based only on the Candidate Evidence.

Candidate most relevant information:
{candidate_context}

Complete source of truth:
{candidate_profile.model_dump_json}
"""

    # --------------------------------------------------------
    # 3. User Prompt
    # --------------------------------------------------------
    user_prompt = f"""
Job Description:
{job_description}

Return ONLY a JSON object matching this schema:
{JobMatch.model_json_schema()}
"""

    # --------------------------------------------------------
    # 4. Groq Request
    # --------------------------------------------------------
    last_error = None

    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                model=GROQ_MODEL,
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_json = response.choices[0].message.content
            validated_data = JobMatch.model_validate_json(raw_json)

            return {
                "success": True,
                "data": validated_data.model_dump(),
            }

        except ValidationError as e:
            last_error = str(e)
            print(f"⚠️ Pydantic validation failed on attempt {attempt + 1}: {e}")
            continue

        except Exception as e:
            last_error = str(e)
            print(f"❌ Groq API error: {e}")
            break

    # --------------------------------------------------------
    # 5. Failed
    # --------------------------------------------------------
    return {
        "success": False,
        "reason": "VALIDATION_FAILED",
        "error": last_error or "Unknown failure",
    }


# ============================================================
# Manual Test
# ============================================================
if __name__ == "__main__":
    sample_jd = """
    Wir suchen einen Werkstudenten für Machine Learning in Berlin.

    Du solltest Erfahrung mit Python, NLP und RAG-Systemen haben.

    React-Kenntnisse sind ein Plus.
    """

    result = analyze_job_match(sample_jd)
    print(result)
