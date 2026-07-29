"""Node: generate answers for form fields.

Static (mapped) fields pull directly from the profile — never invented.
Dynamic (unmapped) fields go through the grounded answer_generation_service.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.agents.state import AgentState
from app.services.answer_generation_service import AnswerGenerationService

logger = logging.getLogger("app.agents.generate_answers")

# File inputs (resume/cover-letter uploads) can't be "answered" with
# generated text — sending them through the grounded-answer LLM always
# produces a nonsensical refusal ("I don't have information...") for what
# is actually a file-attachment step the human has to do, and wastes an LLM
# call in the process.
NON_ANSWERABLE_FIELD_TYPES = {"file"}

# Dynamic-field answers used to be generated one at a time in a sequential
# loop — with N unmapped fields that's N sequential LLM round-trips, which on
# a free-tier model can take minutes for a real application form. They're
# independent of each other, so run them concurrently instead. Capped rather
# than unbounded to stay under free-tier rate limits.
MAX_CONCURRENT_GENERATIONS = 4

CANONICAL_TO_PROFILE_PATH = {
    "name": "full_name",
    "email": "email",
    "phone": "phone",
    "location": "location",
    "linkedin": "linkedin_url",
    "github": "github_url",
    "portfolio": "portfolio_url",
    "twitter": "twitter_url",
    "headline": "headline",
    "summary": "summary",
    "current_company": "current_company",
    "current_job_title": "current_job_title",
    "highest_education": "highest_education",
    "university": "university",
    "graduation_year": "graduation_year",
    "salary": "expected_salary",
    "current_salary": "current_salary",
    "notice_period": "notice_period_days",
    "years_experience": "years_experience",
    "visa_status": "visa_status",
    "willing_to_relocate": "willing_to_relocate",
    "remote_preference": "remote_preference",
    "availability": "availability",
    "cover_letter": "cover_letter",
    "preferred_location": "preferred_locations",
    "preferred_role": "preferred_roles",
    "languages_spoken": "languages_spoken",
    "certifications": "certifications",
    # Personal information
    "first_name": "first_name",
    "middle_name": "middle_name",
    "last_name": "last_name",
    "preferred_name": "preferred_name",
    "legal_name": "legal_name",
    "gender": "gender",
    "date_of_birth": "date_of_birth",
    "nationality": "nationality",
    "marital_status": "marital_status",
    # Contact / address
    "alternate_email": "alternate_email",
    "country_code": "country_code",
    "whatsapp_number": "whatsapp_number",
    "address_line1": "address_line1",
    "address_line2": "address_line2",
    "city": "city",
    "state": "state",
    "country": "country",
    "postal_code": "postal_code",
    # Job preferences
    "employment_type": "employment_type",
    # Community / social links
    "kaggle": "kaggle_url",
    "leetcode": "leetcode_url",
    "hackerrank": "hackerrank_url",
    "codechef": "codechef_url",
    "geeksforgeeks": "geeksforgeeks_url",
    "stackoverflow": "stackoverflow_url",
    "medium": "medium_url",
    # Education detail
    "degree": "degree",
    "specialization": "specialization",
    "current_cgpa": "current_cgpa",
    "percentage": "percentage",
    "tenth_percentage": "tenth_percentage",
    "twelfth_percentage": "twelfth_percentage",
    "academic_achievements": "academic_achievements",
    # Experience detail
    "is_fresher": "is_fresher",
    "relevant_experience": "relevant_experience_years",
    "reason_for_leaving": "reason_for_leaving",
    # Work authorization
    "work_authorized": "work_authorized",
    "requires_visa_sponsorship": "requires_visa_sponsorship",
    "passport_number": "passport_number",
    "citizenship": "citizenship",
    # Voluntary diversity self-identification
    "disability_status": "disability_status",
    "veteran_status": "veteran_status",
    "ethnicity": "ethnicity",
    # Availability
    "immediate_joiner": "immediate_joiner",
    "time_zone": "time_zone",
    # Additional
    "awards": "awards",
    "publications": "publications",
    "hobbies_interests": "hobbies_interests",
}


def _most_relevant_work_experience(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The entry marked "I currently work here", or failing that the one
    with the latest end year — mirrors what a human would treat as their
    "current" job when a form asks a single flat Job Title / Company
    question outside of the repeatable Work Experience section itself.
    """
    entries = profile.get("work_experience") or []
    if not entries:
        return None
    current = [e for e in entries if e.get("is_current")]
    if current:
        return current[0]
    return sorted(entries, key=lambda e: e.get("end_year") or 9999, reverse=True)[0]


def _most_relevant_education(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The education entry with the latest end year — treated as the
    candidate's highest/most recent qualification."""
    entries = profile.get("education_history") or []
    if not entries:
        return None
    return sorted(entries, key=lambda e: e.get("end_year") or 0, reverse=True)[0]


def _profile_value(profile: Dict[str, Any], canonical_key: str) -> Optional[str]:
    path = CANONICAL_TO_PROFILE_PATH.get(canonical_key)
    if not path:
        return None
    value = profile.get(path)

    # Fall back to the structured, repeatable Work Experience / Education
    # history when the flat single-value field wasn't separately filled in —
    # a real gap: a candidate can fill in the "Add Another" work experience
    # section on the Profile page without ever touching the older flat
    # current_company/current_job_title/university/degree fields, and a
    # form asking a plain "Job Title"/"Company"/"University"/"Degree"
    # question outside of a repeatable section should still resolve from
    # that history rather than refuse.
    if value is None and canonical_key in ("current_job_title", "current_company"):
        entry = _most_relevant_work_experience(profile)
        if entry:
            value = entry.get("job_title") if canonical_key == "current_job_title" else entry.get("company")

    if value is None and canonical_key in ("university", "highest_education", "degree"):
        entry = _most_relevant_education(profile)
        if entry:
            value = entry.get("school") if canonical_key == "university" else entry.get("degree")

    # A bare "Name" field maps to the old flat full_name column, but a
    # candidate can fill in first_name/last_name (Personal Information
    # section) without ever touching full_name — fall back to combining
    # them, then to preferred/legal name, rather than refusing a field this
    # trivially answerable.
    if value is None and canonical_key == "name":
        first = profile.get("first_name")
        last = profile.get("last_name")
        combined = " ".join(p for p in (first, last) if p)
        value = combined or profile.get("preferred_name") or profile.get("legal_name")

    if value is None:
        return None
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else None
    return str(value)


async def generate_answers_node(
    state: AgentState, answer_service: AnswerGenerationService
) -> Dict[str, Any]:
    fields = state.get("extracted_fields", [])
    mappings = state.get("field_mappings", {})
    profile = state.get("profile", {})
    retrieved_context = state.get("retrieved_context", [])
    job_description = state.get("job_description", "")
    profile_summary = ", ".join(f"{k}={v}" for k, v in profile.items() if v)

    generated_answers: Dict[str, Dict[str, Any]] = {}
    dynamic_fields: List[Tuple[str, Dict[str, Any], Optional[str]]] = []

    for field in fields:
        field_key = field.get("name") or field.get("label") or ""
        if not field_key:
            continue

        if field.get("type") in NON_ANSWERABLE_FIELD_TYPES:
            generated_answers[field_key] = {
                "answer": "(requires manually attaching a file — not something the agent can fill in)",
                "source": "profile",
                "canonical_key": None,
                "refused": False,
            }
            continue

        canonical_key = mappings.get(field_key)

        if canonical_key:
            value = _profile_value(profile, canonical_key)
            if value is not None:
                generated_answers[field_key] = {
                    "answer": value,
                    "source": "profile",
                    "canonical_key": canonical_key,
                    "refused": False,
                }
                continue

        dynamic_fields.append((field_key, field, canonical_key))

    if dynamic_fields:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATIONS)

        async def _generate_one(
            field_key: str, field: Dict[str, Any], canonical_key: Optional[str]
        ) -> Tuple[str, Dict[str, Any]]:
            label = field.get("label") or field.get("placeholder") or field_key
            async with semaphore:
                result = await answer_service.generate_answer(
                    field_label=label,
                    field_type=field.get("type", "text"),
                    job_description=job_description,
                    retrieved_context=retrieved_context,
                    profile_summary=profile_summary,
                )
            return field_key, {
                "answer": result.answer,
                "source": "generated",
                "canonical_key": canonical_key,
                "refused": result.refused,
                "reasoning": result.reasoning,
            }

        results = await asyncio.gather(*(_generate_one(*args) for args in dynamic_fields))
        for field_key, entry in results:
            generated_answers[field_key] = entry

    return {"generated_answers": generated_answers}


def make_generate_answers_node(answer_service: AnswerGenerationService):
    async def _node(state: AgentState) -> Dict[str, Any]:
        return await generate_answers_node(state, answer_service)

    return _node
