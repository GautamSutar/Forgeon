from __future__ import annotations

from pathlib import Path

from app.services.resume_parser_service import (
    extract_contact_info,
    extract_hyperlinks_from_pdf,
    extract_links,
    extract_text_from_pdf,
    parse_resume_pdf,
    parse_skills,
    segment_sections,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

SAMPLE_RESUME_TEXT = """Jane Doe
jane.doe@example.com
(555) 123-4567

SKILLS
Python, FastAPI, SQL, Docker

EXPERIENCE
Senior Engineer at Acme Corp
- Built the core API
- Led a team of 4

EDUCATION
BS Computer Science, State University

CERTIFICATIONS
AWS Certified Solutions Architect

LINKS
https://github.com/janedoe https://linkedin.com/in/janedoe
"""


def test_extract_contact_info_finds_email_and_phone() -> None:
    contact = extract_contact_info(SAMPLE_RESUME_TEXT)
    assert contact.email == "jane.doe@example.com"
    assert contact.phone is not None
    assert contact.name == "Jane Doe"


def test_segment_sections_splits_correctly() -> None:
    sections = segment_sections(SAMPLE_RESUME_TEXT)
    assert any("Python" in line for line in sections["skills"])
    assert any("Acme Corp" in line for line in sections["experience"])
    assert any("State University" in line for line in sections["education"])
    assert any("AWS Certified" in line for line in sections["certifications"])


def test_parse_skills_splits_on_delimiters() -> None:
    skills = parse_skills(["Python, FastAPI, SQL, Docker"])
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "SQL" in skills
    assert "Docker" in skills


def test_extract_links_finds_urls() -> None:
    links = extract_links(SAMPLE_RESUME_TEXT)
    assert any("github.com/janedoe" in link for link in links)
    assert any("linkedin.com/in/janedoe" in link for link in links)


def test_no_hallucination_only_extracted_content_present() -> None:
    """Guard against invented content: nothing not present in raw text should
    appear in any parsed field."""
    sections = segment_sections(SAMPLE_RESUME_TEXT)
    for section_lines in sections.values():
        for line in section_lines:
            assert line in SAMPLE_RESUME_TEXT


# --- Real two-column resume regression coverage -----------------------------
#
# Two-column layouts are extremely common and pdfplumber's default
# extract_text() interleaves the columns line-by-line by vertical position,
# producing garbled text that breaks section-header detection. These tests
# pin the fix against a synthetic (fabricated data) two-column PDF fixture
# that reproduces the same structural properties as the real-world resume
# that originally exposed the bug — full-width header/summary above a
# two-column body, section headers landing on the same row across columns,
# and hyperlink annotations — without containing any real personal data.

SYNTHETIC_RESUME_PDF = FIXTURES_DIR / "synthetic_two_column_resume.pdf"


def _synthetic_resume_bytes() -> bytes:
    return SYNTHETIC_RESUME_PDF.read_bytes()


def test_two_column_resume_extracts_columns_without_interleaving() -> None:
    raw_text = extract_text_from_pdf(_synthetic_resume_bytes())

    # The full-width summary paragraph above the two-column body must stay
    # intact as one continuous line, not be shredded by the column gutter.
    assert "Backend & AI Developer with hands-on experience building REST APIs, backend services," in raw_text

    # Left-column and right-column section headers must not be merged onto
    # the same line (the original bug produced "EXPERIENCE KEY ACHIEVEMENTS").
    assert "EXPERIENCE KEY ACHIEVEMENTS" not in raw_text
    assert "\nEXPERIENCE\n" in raw_text
    assert "\nKEY ACHIEVEMENTS\n" in raw_text
    assert "\nSKILLS\n" in raw_text
    assert "\nPERSONAL PROJECTS\n" in raw_text


def test_two_column_resume_contact_info() -> None:
    parsed = parse_resume_pdf(_synthetic_resume_bytes())
    assert parsed.contact.name == "Alex Morgan"
    assert parsed.contact.email == "alex.morgan.dev@example.com"
    assert parsed.contact.phone is not None


def test_two_column_resume_skills_are_not_cross_contaminated_with_projects() -> None:
    parsed = parse_resume_pdf(_synthetic_resume_bytes())
    skills_blob = " ".join(parsed.skills)
    # These phrases belong to the PERSONAL PROJECTS column, not SKILLS —
    # regression guard for the column-interleaving bug.
    assert "glassmorphism" not in skills_blob
    assert "full-stack AI chat platform" not in skills_blob
    assert any("FastAPI" in s for s in parsed.skills)
    assert any("LangChain" in s for s in parsed.skills)


def test_two_column_resume_education_excludes_achievements() -> None:
    parsed = parse_resume_pdf(_synthetic_resume_bytes())
    education_blob = " ".join(entry["header"] for entry in parsed.education)
    assert "Ridgeway" not in education_blob
    assert "Riverbend" in education_blob


def test_two_column_resume_projects_section_populated() -> None:
    parsed = parse_resume_pdf(_synthetic_resume_bytes())
    project_headers = [entry["header"] for entry in parsed.projects]
    assert any("TaskFlow" in h for h in project_headers)
    assert any("StudyBuddy" in h for h in project_headers)


def test_two_column_resume_hyperlinks_extracted() -> None:
    links = extract_hyperlinks_from_pdf(_synthetic_resume_bytes())
    assert any("github.com/alexmorgan-dev" in link for link in links)
    assert any("linkedin.com/in/alexmorgan-dev" in link for link in links)
