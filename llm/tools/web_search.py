from llm.client import get_llm_client

llm = get_llm_client()


def research_company(company_name: str, job_description: str, job_title: str) -> str:
    """
    Returns plain-text company research (official site, summary, products, relevant tech)
    for direct injection into resume/cover-letter prompts. No structured extraction —
    if you later need individual fields (e.g. to store separately in Supabase), add a
    second structured_completion call, but don't pay for it until you actually need it.
    """
    search_prompt = f"""Research the company "{company_name}" for someone preparing a job
application for the role "{job_title}" there.

Find:
- The official company website
- A short summary of what the company does
- Their main products/services
- Technologies, tools, or technical topics relevant to this role

Job description for relevance context:
{job_description}

Be factual and concise. Only report what you actually find — do not speculate. Mention the
URLs of the pages you used directly in your answer."""

    search_result = llm.browser_search_query(
        search_prompt,
        model="openai/gpt-oss-20b",
        reasoning_effort="low",
    )

    return search_result["content"].strip()