import os
import json
import numpy as np
from pydantic import BaseModel, ValidationError
from groq import Groq
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm
from dotenv import load_dotenv

from scraper.embeddings import EMBEDDINGS_CACHE_PATH, CHUNKS_CACHE_PATH  # reuse the same paths

load_dotenv()


class TailoredResume(BaseModel):
    company_name: str
    company_location: str
    match_score: int  # 0-100, Groq's holistic judgment (not the cosine similarity number)
    match_reasoning: str
    tailored_bullet_1: str
    tailored_bullet_2: str
    tailored_bullet_3: str

    @property
    def is_worth_reviewing(self) -> bool:
        return self.match_score >= 50  # tune this threshold to taste


# Cheap pre-filter threshold on cosine similarity, BEFORE spending a Groq API call.
# This is deliberately conservative (low) since cosine similarity is a rough proxy,
# not a real judgment — it's just meant to catch obviously irrelevant jobs early.
SIMILARITY_GATE_THRESHOLD = 0.25


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Lazy-loaded globals — populated on first call, not at import time,
# so importing this module doesn't crash if the cache doesn't exist yet.
_embedder = None
_resume_embeddings = None
_resume_chunks = None


def _ensure_loaded():
    global _embedder, _resume_embeddings, _resume_chunks
    if _embedder is None:
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    if _resume_embeddings is None or _resume_chunks is None:
        if not EMBEDDINGS_CACHE_PATH.exists() or not CHUNKS_CACHE_PATH.exists():
            raise RuntimeError(
                "Embedding cache missing. Run 'python -m scraper.embeddings_fixed' first."
            )
        _resume_embeddings = np.load(EMBEDDINGS_CACHE_PATH)
        with open(CHUNKS_CACHE_PATH, "r", encoding="utf-8") as f:
            _resume_chunks = json.load(f)


def get_relevant_chunks(job_description: str, top_k: int = 4) -> tuple[str, float]:
    """
    Computes cosine similarity in-memory and returns:
    - the formatted text of the most relevant resume chunks
    - the MAX similarity score among them (cheap relevance signal, used as a pre-filter gate —
      NOT the same as Groq's match_score, which is a full judgment, not a distance metric)
    """
    _ensure_loaded()
    jd_embedding = _embedder.encode(job_description)

    similarities = np.dot(_resume_embeddings, jd_embedding) / (
        norm(_resume_embeddings, axis=1) * norm(jd_embedding)
    )
    top_indices = np.argsort(similarities)[::-1][:top_k]
    max_similarity = float(similarities[top_indices[0]]) if len(top_indices) else 0.0

    chunks_text = "\n\n".join(
        f"--- RELEVANT EXPERIENCE ---\n{_resume_chunks[i]['content']}" for i in top_indices
    )
    return chunks_text, max_similarity


def generate_tailored_content(job_description: str, max_retries: int = 3) -> dict:
    """
    Passes retrieved chunks and JD to Groq, forces JSON, and validates via Pydantic.

    Returns one of:
      {"success": True, "data": {...}}
      {"success": False, "reason": "LOW_SIMILARITY", "similarity_score": float}   # skipped, no API call spent
      {"success": False, "reason": "VALIDATION_FAILED", "error": "..."}

    No silent placeholder fallback: bad or low-relevance output should never look like a real result.
    """
    relevant_experience, similarity_score = get_relevant_chunks(job_description)

    # Cheap pre-filter: skip the Groq call entirely for obviously irrelevant jobs.
    if similarity_score < SIMILARITY_GATE_THRESHOLD:
        print(f"⏭️  Skipping Groq call — low similarity ({similarity_score:.3f})")
        return {
            "success": False,
            "reason": "LOW_SIMILARITY",
            "similarity_score": similarity_score,
        }

    system_prompt = f"""
    You are an expert technical recruiter in Germany. Your task is to (1) judge how well this
    candidate genuinely fits this job, and (2) write a tailored cover letter (A2/B1 level German)
    aligning the candidate's real skills with the job description.

    CRITICAL GROUNDING RULE: You MUST write this letter using ONLY the facts present in the provided
    Candidate Experience. Do not invent, fabricate, or embellish experience not explicitly stated.

    For match_score (0-100) and match_reasoning: judge holistically based on the FULL job description
    and the candidate experience below — required skills, seniority level, language/location
    requirements, etc. Be honest and critical; do not default to a high score.

    Candidate Experience:
    {relevant_experience}
    """

    user_prompt = f"""
    Job Description:
    {job_description}

    Output strictly as a JSON object matching this schema:
    {TailoredResume.model_json_schema()}
    """

    last_error = None
    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw_json_str = response.choices[0].message.content
            validated_data = TailoredResume.model_validate_json(raw_json_str)
            return {"success": True, "data": validated_data.model_dump()}

        except ValidationError as e:
            last_error = str(e)
            print(f"⚠️  Pydantic validation failed on attempt {attempt + 1}: {e}")
            continue
        except Exception as e:
            last_error = str(e)
            print(f"❌ Unexpected Groq API error: {e}")
            break

    # No silent fallback — surface the failure so it can be flagged in the DB
    # (e.g. applications.status = 'NEEDS_REVIEW') rather than inserted as if real.
    return {
        "success": False,
        "reason": "VALIDATION_FAILED",
        "error": last_error or "Unknown failure after retries",
    }


if __name__ == "__main__":
    sample_jd = (
        "Wir suchen einen Werkstudenten für Machine Learning in Berlin. "
        "Du solltest Erfahrung mit Python, NLP und RAG-Systemen haben. "
        "React-Kenntnisse sind ein Plus."
    )
    result = generate_tailored_content(sample_jd)
    print(json.dumps(result, indent=2, ensure_ascii=False))