import os

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, ValidationError

from rag.retriever import (
    get_relevant_chunks,
    SIMILARITY_GATE_THRESHOLD,
)

load_dotenv()


# --------------------------------------------------
# Configuration
# --------------------------------------------------

GROQ_MODEL = "llama-3.3-70b-versatile"

MAX_RETRIES = 3


# --------------------------------------------------
# Output schema
# --------------------------------------------------


class TailoredResume(BaseModel):

    company_name: str
    company_location: str
    match_score: int
    match_reasoning: str
    tailored_bullet_1: str
    tailored_bullet_2: str
    tailored_bullet_3: str


# --------------------------------------------------
# Groq client
# --------------------------------------------------

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --------------------------------------------------
# Main function
# --------------------------------------------------


def generate_tailored_content(job_description: str, max_retries: int = MAX_RETRIES) -> dict:
    """
    Retrieve relevant candidate experience and use Groq to evaluate the job and
    generate tailored content.
    """

    # ----------------------------------------------
    # 1. Retrieve relevant resume experience
    # ----------------------------------------------

    (relevant_experience, similarity_score) = get_relevant_chunks(job_description)

    # ----------------------------------------------
    # 2. Cheap relevance gate
    # ----------------------------------------------

    if similarity_score < SIMILARITY_GATE_THRESHOLD:

        print("⏭️ Skipping Groq call — " f"low similarity " f"({similarity_score:.3f})")

        return {
            "success": False,
            "reason": "LOW_SIMILARITY",
            "similarity_score": similarity_score,
        }

    # ----------------------------------------------
    # 3. System prompt
    # ----------------------------------------------

    system_prompt = f"""
You are an expert technical recruiter
evaluating a candidate for a job in Germany.

Your task is to:

1. Judge how well the candidate fits the job.
2. Give an honest match score from 0 to 100.
3. Explain the main reasons for the score.
4. Create tailored experience bullets.

IMPORTANT GROUNDING RULE:

You MUST use ONLY facts explicitly
present in the Candidate Experience.

Never:

- invent experience
- invent technologies
- invent years of experience
- exaggerate responsibilities
- claim professional experience that is
  not explicitly provided
- claim fluent German unless explicitly stated

Be honest and critical.

Candidate Experience:

{relevant_experience}
"""

    # ----------------------------------------------
    # 4. User prompt
    # ----------------------------------------------

    user_prompt = f"""
Job Description:

{job_description}

Return ONLY a JSON object matching
this schema:

{TailoredResume.model_json_schema()}
"""

    # ----------------------------------------------
    # 5. Groq call
    # ----------------------------------------------

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

            validated_data = TailoredResume.model_validate_json(raw_json)

            return {
                "success": True,
                "data": validated_data.model_dump(),
            }

        except ValidationError as e:

            last_error = str(e)
            print("⚠️ Pydantic validation failed " f"on attempt {attempt + 1}: " f"{e}")
            continue

        except Exception as e:

            last_error = str(e)
            print(f"❌ Groq API error: {e}")
            break

    # ----------------------------------------------
    # 6. Failed
    # ----------------------------------------------

    return {
        "success": False,
        "reason": "VALIDATION_FAILED",
        "error": (last_error or "Unknown failure"),
    }


if __name__ == "__main__":

    sample_jd = """
    Wir suchen einen Werkstudenten
    für Machine Learning in Berlin.

    Du solltest Erfahrung mit Python,
    NLP und RAG-Systemen haben.

    React-Kenntnisse sind ein Plus.
    """

    result = generate_tailored_content(sample_jd)

    print(result)
