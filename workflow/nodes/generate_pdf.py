from workflow.pdf_generator import (
    generate_resume_pdf,
    generate_cover_letter_pdf,
    save_pdf_locally,
)


def generate_pdfs(state):
    """
    Renders the tailored resume and cover letter to PDF and saves them locally.
    Populates state.resume_pdf_path / state.cover_letter_pdf_path with the file paths.
    Swap `save_pdf_locally` for a Supabase upload later — the rest of this node stays
    the same, since it just needs to return a string (path or URL) either way.
    """
    if state.tailored_resume is None:
        state.errors.append("generate_pdfs: tailored_resume is missing on state.")
        return state
    if state.cover_letter is None:
        state.errors.append("generate_pdfs: cover_letter is missing on state.")
        return state

    try:
        resume_bytes = generate_resume_pdf(state.tailored_resume)
        cover_letter_bytes = generate_cover_letter_pdf(
            letter=state.cover_letter,
            sender=state.tailored_resume.profile_header,
        )

        state.resume_pdf_path = save_pdf_locally(
            resume_bytes, state.company_name, state.job_title, "resume"
        )
        state.cover_letter_pdf_path = save_pdf_locally(
            cover_letter_bytes, state.company_name, state.job_title, "cover_letter"
        )

    except Exception as e:
        state.errors.append(f"generate_pdfs failed: {e}")

    return state
