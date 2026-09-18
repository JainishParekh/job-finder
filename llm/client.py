import os
import time
from typing import Type, TypeVar, Literal, Optional
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, ValidationError

load_dotenv()
T = TypeVar("T", bound=BaseModel)


class GroqLLMClient:
    """Single entry point for all LLM calls (job matching, resume, cover letter, research).
    Instantiate once and reuse — e.g. `llm = GroqLLMClient()` at module level in each file,
    or via `get_llm_client()` below for a shared singleton."""

    def __init__(self, model: str = "openai/gpt-oss-120b", max_retries: int = 3):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
        self.max_retries = max_retries

    # ----------------------------------------------------------------
    # Mode 1: plain structured generation (job match, resume, cover letter)
    # ----------------------------------------------------------------
    def structured_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        temperature: float = 0.2,
        max_retries: Optional[int] = None,
    ) -> T:
        """JSON-mode completion validated against `schema`. On a validation error,
        the error is fed back to the model so the retry actually corrects course
        (rather than blindly repeating the same prompt)."""
        max_retries = max_retries or self.max_retries
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"{user_prompt}\n\nReturn ONLY a JSON object matching this schema:\n{schema.model_json_schema()}",
            },
        ]

        last_error: Exception | None = None
        raw: str | None = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=temperature,
                )
                raw = response.choices[0].message.content
                return schema.model_validate_json(raw)

            except ValidationError as e:
                last_error = e
                print(f"⚠️ Validation failed on attempt {attempt + 1}: {e}")
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": f"That JSON failed schema validation:\n{e}\n\nReturn ONLY the corrected JSON object.",
                    }
                )

            except Exception as e:
                last_error = e
                print(f"❌ Groq API error on attempt {attempt + 1}: {e}")
                time.sleep(1.5 * (attempt + 1))

        raise RuntimeError(
            f"structured_completion({schema.__name__}) failed after {max_retries} attempts: {last_error}"
        )

    # ----------------------------------------------------------------
    # Mode 2: agentic tool-calling (company research w/ browser search)
    # ----------------------------------------------------------------
    def browser_search_query(
        self,
        prompt: str,
        model: str = "openai/gpt-oss-20b",
        reasoning_effort: Literal['none', 'default', 'low', 'medium', 'high'] = "low",
        max_completion_tokens: int = 2048,
    ) -> dict:
        """Runs Groq's built-in browser-search tool (Exa-backed, server-side, interactive
        browsing rather than a single snippet search). Only supported on gpt-oss models.

        IMPORTANT: browser_search is NOT compatible with structured outputs / custom tools
        in the same call — that's what caused earlier 400 errors when custom submit tools
        were mixed in. Use this to gather research as plain text, then run
        `structured_completion` as a SEPARATE call to extract it into a schema.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=max_completion_tokens,
            top_p=1,
            reasoning_effort=reasoning_effort,
            tool_choice="required",
            tools=[{"type": "browser_search"}],
        )
        msg = response.choices[0].message

        # Attempt to pull structured source URLs if the SDK exposes them on executed_tools;
        # field names for browser_search aren't fully documented, so this degrades gracefully.
        sources: list[str] = []
        for executed_tool in getattr(msg, "executed_tools", None) or []:
            for attr_name in ("browser_search_results", "search_results"):
                results_obj = getattr(executed_tool, attr_name, None)
                if not results_obj:
                    continue
                results = getattr(results_obj, "results", None) or []
                for r in results:
                    url = (
                        getattr(r, "url", None)
                        if not isinstance(r, dict)
                        else r.get("url")
                    )
                    if url:
                        sources.append(url)

        return {
            "content": msg.content or "",
            "sources": list(dict.fromkeys(sources)),
        }


# ----------------------------------------------------------------
# Shared singleton — import `get_llm_client()` anywhere you need it
# ----------------------------------------------------------------
_client_instance: Optional[GroqLLMClient] = None


def get_llm_client(model: str = os.getenv("GROQ_MODEL_NAME")) -> GroqLLMClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = GroqLLMClient(model=model)
    return _client_instance
