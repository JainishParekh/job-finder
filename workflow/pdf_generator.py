from pathlib import Path
from datetime import date
from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML
import tempfile
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from schemas.tailored_resume import TailoredResume
from schemas.cover_letter import CoverLetter

TEMPLATES_DIR = Path(__file__).parent / "template"
OUTPUT_DIR = Path(__file__).parent / "generated_documents"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def _html_to_pdf_bytes(html_str: str, base_url: str | None = None) -> bytes:
    """Renders HTML to PDF using headless Chromium via Playwright.
    Writing to a temp .html file (rather than a data: URL) lets relative asset
    paths — like profile_image — resolve correctly against base_url, same as
    WeasyPrint's base_url parameter did."""
    base_dir = Path(base_url) if base_url else Path.cwd()

    with tempfile.NamedTemporaryFile(
        suffix=".html", dir=base_dir, delete=False, mode="w", encoding="utf-8"
    ) as tmp:
        tmp.write(html_str)
        tmp_path = tmp.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file:///{tmp_path}")
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                # your templates already set @page margins in CSS, so keep these at 0
                # to avoid doubling up on whitespace
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            browser.close()
        return pdf_bytes
    finally:
        os.remove(tmp_path)


# def _html_to_pdf_bytes(html_str: str, base_url: str | None = None) -> bytes:
#     return HTML(string=html_str, base_url=base_url).write_pdf()


def generate_resume_pdf(resume: TailoredResume) -> bytes:
    template = env.get_template("resume.html")
    html_out = template.render(resume=resume)
    # base_url lets relative profile_image paths resolve; use TEMPLATES_DIR or an
    # absolute image URL directly in profile_image if you're storing it in Supabase Storage
    return _html_to_pdf_bytes(html_out, base_url=str(TEMPLATES_DIR))


def generate_cover_letter_pdf(
    letter: CoverLetter,
    sender: TailoredResume,  # pass resume.profile_header, or candidate_profile directly
    letter_date: str | None = None,
) -> bytes:
    template = env.get_template("cover_letter.html")
    html_out = template.render(
        letter=letter,
        sender=sender,  # expects .full_name, .address, .phone_number, .email
        letter_date=letter_date or date.today().strftime("%d.%m.%Y"),
    )
    return _html_to_pdf_bytes(html_out, base_url=str(TEMPLATES_DIR))


def _safe_slug(text: str) -> str:
    """Filesystem-safe slug for filenames, e.g. 'Sopra Steria' -> 'sopra-steria'."""
    keep = "".join(c if c.isalnum() or c in " -" else "" for c in text)
    return "-".join(keep.lower().split())


def save_pdf_locally(
    pdf_bytes: bytes, company_name: str, job_title: str, doc_type: str
) -> str:
    """Saves PDF bytes to OUTPUT_DIR and returns the local file path as a string.
    Directory structure: generated_documents/<company>-<job-title>/<doc_type>.pdf
    """
    folder_name = f"{_safe_slug(company_name)}-{_safe_slug(job_title)}"
    target_dir = OUTPUT_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / f"{doc_type}.pdf"
    file_path.write_bytes(pdf_bytes)

    return str(file_path.resolve())
