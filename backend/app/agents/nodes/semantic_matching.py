"""Node: map form field labels to canonical profile keys via embedding similarity.

Uses cosine similarity between the embedding of each field label and the
embeddings of a fixed canonical taxonomy — NOT string matching.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from app.agents.state import AgentState
from app.llm.client import LLMClient

logger = logging.getLogger("app.agents.semantic_matching")

CANONICAL_FIELD_TAXONOMY: List[str] = [
    "name",
    "email",
    "phone",
    "location",
    "linkedin",
    "github",
    "portfolio",
    "twitter",
    "headline",
    "summary",
    "current_company",
    "current_job_title",
    "highest_education",
    "university",
    "graduation_year",
    "salary",
    "current_salary",
    "notice_period",
    "years_experience",
    "visa_status",
    "willing_to_relocate",
    "remote_preference",
    "availability",
    "cover_letter",
    "preferred_location",
    "preferred_role",
    "languages_spoken",
    "certifications",
    # Personal information
    "first_name",
    "middle_name",
    "last_name",
    "preferred_name",
    "legal_name",
    "gender",
    "date_of_birth",
    "nationality",
    "marital_status",
    # Contact / address (more specific than "location" — check these first)
    "alternate_email",
    "country_code",
    "whatsapp_number",
    "address_line1",
    "address_line2",
    "city",
    "state",
    "country",
    "postal_code",
    # Job preferences
    "employment_type",
    # Community / social links
    "kaggle",
    "leetcode",
    "hackerrank",
    "codechef",
    "geeksforgeeks",
    "stackoverflow",
    "medium",
    # Education detail (more specific than "highest_education" — check first)
    "degree",
    "specialization",
    "current_cgpa",
    "percentage",
    "tenth_percentage",
    "twelfth_percentage",
    "academic_achievements",
    # Experience detail
    "is_fresher",
    "relevant_experience",
    "reason_for_leaving",
    # Work authorization (more specific than "visa_status" — check first)
    "work_authorized",
    "requires_visa_sponsorship",
    "passport_number",
    "citizenship",
    # Voluntary diversity self-identification
    "disability_status",
    "veteran_status",
    "ethnicity",
    # Availability
    "immediate_joiner",
    "time_zone",
    # Additional
    "awards",
    "publications",
    "hobbies_interests",
]

SIMILARITY_THRESHOLD = 0.72

# Fallback for when embeddings aren't available at all (e.g. a chat-only
# provider like OpenRouter with no separate embeddings key configured).
# Without this, every field — including trivially static ones like "Email"
# or "LinkedIn URL" — falls through to per-field LLM generation instead of
# being pulled straight from the profile, which is both slower (one LLM
# round-trip per field instead of zero) and less correct.
_KEYWORD_PATTERNS: Dict[str, List[str]] = {
    # --- Long / multi-word phrases first — these are specific enough that
    # order among themselves mostly doesn't matter, but they MUST all come
    # before the short single-word patterns below (e.g. "country", "state"),
    # since a sentence like "Are you legally authorized to work in this
    # country?" would otherwise get caught by the generic "country" pattern
    # before ever reaching "work_authorized". ---
    "is_fresher": ["are you a fresher", "fresher or experienced", "fresher/experienced"],
    "relevant_experience": ["relevant experience"],
    "reason_for_leaving": ["reason for leaving"],
    "work_authorized": ["authorized to work", "work authorization status", "legally authorized"],
    "requires_visa_sponsorship": ["require visa sponsorship", "need sponsorship", "visa sponsorship"],
    "passport_number": ["passport number"],
    "disability_status": ["disability status", "disability"],
    "veteran_status": ["veteran status", "veteran"],
    "immediate_joiner": ["immediate joiner"],
    "time_zone": ["time zone", "timezone"],
    "date_of_birth": ["date of birth", "birth date", "dob"],
    "marital_status": ["marital status"],
    "alternate_email": ["alternate email", "secondary email"],
    "country_code": ["country code", "dial code"],
    "whatsapp_number": ["whatsapp"],
    "address_line1": ["address line 1", "street address", "address line1"],
    "address_line2": ["address line 2", "apartment", "address line2"],
    "postal_code": ["postal code", "zip code", "zip"],
    "employment_type": ["employment type", "full-time", "part-time", "full time", "part time"],
    "academic_achievements": ["academic achievement"],
    "current_cgpa": ["cgpa", "gpa"],
    "tenth_percentage": ["10th percentage", "tenth percentage", "class x", "ssc"],
    "twelfth_percentage": ["12th percentage", "twelfth percentage", "class xii", "hsc"],
    "first_name": ["first name", "given name"],
    "middle_name": ["middle name"],
    "last_name": ["last name", "family name", "surname"],
    "preferred_name": ["preferred name"],
    "legal_name": ["legal name"],
    "kaggle": ["kaggle"],
    "leetcode": ["leetcode"],
    "hackerrank": ["hackerrank"],
    "codechef": ["codechef"],
    "geeksforgeeks": ["geeksforgeeks", "gfg"],
    "stackoverflow": ["stack overflow", "stackoverflow"],
    "medium": ["medium profile", "medium.com"],
    "degree": ["degree", "branch"],
    "specialization": ["specialization", "major"],
    "publications": ["publications", "research papers"],
    "hobbies_interests": ["hobbies", "interests"],
    # --- Short single-word / generic patterns last — checked only after
    # everything more specific above has already had a chance to match. ---
    "gender": ["gender", "sex"],
    "nationality": ["nationality"],
    "city": ["city"],
    "state": ["state", "province"],
    "country": ["country"],
    "citizenship": ["citizenship"],
    "ethnicity": ["ethnicity", "race"],
    "percentage": ["percentage"],
    "awards": ["awards"],
    # --- Original / broader patterns ---
    "name": ["full name", "your name", "candidate name"],
    "email": ["email"],
    "phone": ["phone", "mobile", "contact number"],
    "location": ["location", "current location", "address"],
    "linkedin": ["linkedin"],
    "github": ["github"],
    "portfolio": ["portfolio", "personal website", "personal site"],
    "twitter": ["twitter", "x profile", "x.com"],
    "headline": ["headline", "professional title", "tagline"],
    "summary": ["summary", "about you", "bio", "professional summary"],
    "current_company": ["current company", "current employer", "employer name", "company name", "company"],
    "current_job_title": [
        "current title",
        "current job title",
        "current role",
        "current position",
        "job title",
    ],
    "highest_education": ["highest education", "education level", "highest qualification"],
    "university": ["university", "college", "school name", "institution"],
    "graduation_year": ["graduation year", "year of graduation", "grad year"],
    "salary": ["expected salary", "salary expectation", "expected compensation", "desired salary"],
    "current_salary": ["current salary", "current ctc", "current compensation"],
    "notice_period": ["notice period", "notice"],
    "years_experience": ["years of experience", "years experience", "total experience"],
    "visa_status": ["visa status", "visa"],
    "willing_to_relocate": ["willing to relocate", "open to relocation", "relocate"],
    "remote_preference": ["remote", "work location preference", "onsite or remote"],
    "availability": ["availability", "start date", "earliest start date", "when can you start"],
    "cover_letter": ["cover letter", "motivation letter"],
    "preferred_location": ["preferred location", "preferred locations"],
    "preferred_role": ["preferred role", "desired role", "position applying"],
    "languages_spoken": ["languages spoken", "language proficiency", "spoken languages"],
    "certifications": ["certifications", "licenses", "certificates"],
}


def _normalize_label(label: str) -> str:
    """Inserts spaces at camelCase boundaries before lowercasing, so a raw
    attribute-style label like "jobTitle" or "companyName" — what extraction
    falls back to when a field has no real <label>/aria-label, common in
    JS-heavy ATS UIs like Workday — matches the same keyword patterns as a
    human-written label like "Job Title".
    """
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", label)
    return spaced.strip().lower()


def _keyword_match(label: str) -> Optional[str]:
    # Check both forms: the plain lowercased label (so real words that
    # happen to contain capitals mid-word, like "LinkedIn", aren't wrongly
    # split into "Linked In") and the camelCase-split form (so raw
    # attribute-style labels like "jobTitle" still match "job title").
    original = label.strip().lower()
    camel_split = _normalize_label(label)
    if not original:
        return None
    for canonical_key, patterns in _KEYWORD_PATTERNS.items():
        for pattern in patterns:
            if pattern in original or pattern in camel_split:
                return canonical_key
    return None


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def semantic_matching_node(state: AgentState, llm_client: LLMClient) -> Dict[str, Any]:
    fields = state.get("extracted_fields", [])
    labels = [(f.get("label") or f.get("placeholder") or f.get("name") or "") for f in fields]
    non_empty_labels = [lbl for lbl in labels if lbl.strip()]

    if not non_empty_labels:
        return {"field_mappings": {}}

    try:
        canonical_vectors = await llm_client.embed(CANONICAL_FIELD_TAXONOMY)
        label_vectors = await llm_client.embed(non_empty_labels)
    except Exception as exc:
        logger.warning(
            "Embedding call failed during semantic matching (falling back to keyword matching): %s", exc
        )
        mappings: Dict[str, Optional[str]] = {}
        for field in fields:
            label = field.get("label") or field.get("placeholder") or field.get("name") or ""
            field_key = field.get("name") or label
            mappings[field_key] = _keyword_match(label)
        return {"field_mappings": mappings}

    label_to_vector = dict(zip(non_empty_labels, label_vectors))
    mappings: Dict[str, Optional[str]] = {}

    for field in fields:
        label = field.get("label") or field.get("placeholder") or field.get("name") or ""
        field_key = field.get("name") or label
        if not label.strip() or label not in label_to_vector:
            mappings[field_key] = None
            continue

        vector = label_to_vector[label]
        best_key: Optional[str] = None
        best_score = 0.0
        for canonical_key, canonical_vector in zip(CANONICAL_FIELD_TAXONOMY, canonical_vectors):
            score = _cosine_similarity(vector, canonical_vector)
            if score > best_score:
                best_score = score
                best_key = canonical_key

        mappings[field_key] = best_key if best_score >= SIMILARITY_THRESHOLD else None

    return {"field_mappings": mappings}


def make_semantic_matching_node(llm_client: LLMClient):
    async def _node(state: AgentState) -> Dict[str, Any]:
        return await semantic_matching_node(state, llm_client)

    return _node
