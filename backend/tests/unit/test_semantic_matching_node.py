from __future__ import annotations

from typing import List

import pytest

from app.agents.nodes.semantic_matching import (
    CANONICAL_FIELD_TAXONOMY,
    semantic_matching_node,
)
from app.llm.client import LLMClient


class MockEmbeddingLLM(LLMClient):
    """Returns embeddings such that 'Email Address' matches 'email' exactly,
    and a totally unrelated label matches nothing above threshold."""

    def __init__(self) -> None:
        super().__init__(model="mock", api_key="mock")

    async def embed(self, texts: List[str], *, model=None) -> List[List[float]]:  # type: ignore[override]
        vectors = []
        for text in texts:
            if text in CANONICAL_FIELD_TAXONOMY:
                # one-hot vector keyed by taxonomy index
                idx = CANONICAL_FIELD_TAXONOMY.index(text)
            elif "email" in text.lower():
                idx = CANONICAL_FIELD_TAXONOMY.index("email")
            elif "linkedin" in text.lower():
                idx = CANONICAL_FIELD_TAXONOMY.index("linkedin")
            else:
                idx = None

            dim = len(CANONICAL_FIELD_TAXONOMY)
            vec = [0.0] * dim
            if idx is not None:
                vec[idx] = 1.0
            else:
                # near-orthogonal noise vector -> low similarity to everything
                vec = [0.001] * dim
            vectors.append(vec)
        return vectors


@pytest.mark.asyncio
async def test_semantic_matching_maps_email_field() -> None:
    state = {
        "extracted_fields": [
            {"name": "email_field", "label": "Email Address", "type": "email"},
            {"name": "linkedin_field", "label": "LinkedIn Profile URL", "type": "text"},
            {"name": "essay_field", "label": "Tell us about a challenge you overcame", "type": "textarea"},
        ]
    }
    result = await semantic_matching_node(state, MockEmbeddingLLM())
    mappings = result["field_mappings"]

    assert mappings["email_field"] == "email"
    assert mappings["linkedin_field"] == "linkedin"
    assert mappings["essay_field"] is None


@pytest.mark.asyncio
async def test_semantic_matching_handles_no_fields() -> None:
    result = await semantic_matching_node({"extracted_fields": []}, MockEmbeddingLLM())
    assert result["field_mappings"] == {}


class EmbeddingUnavailableLLM(LLMClient):
    """Simulates a chat-only provider (e.g. OpenRouter with no separate
    embeddings key) — embed() always raises, exactly what happens in
    production when only a chat completions endpoint is configured.
    """

    def __init__(self) -> None:
        super().__init__(model="mock", api_key="mock")

    async def embed(self, texts: List[str], *, model=None) -> List[List[float]]:  # type: ignore[override]
        raise RuntimeError("Missing credentials for embeddings endpoint")


@pytest.mark.asyncio
async def test_semantic_matching_falls_back_to_keywords_when_embeddings_unavailable() -> None:
    """Regression test for a real production incident: when embeddings fail
    entirely, every field — including trivially static ones like LinkedIn
    URL or Email — must not silently become unmapped (which would push them
    through slow, unnecessary per-field LLM generation instead of a direct
    profile lookup)."""
    state = {
        "extracted_fields": [
            {"name": "email_field", "label": "Email Address", "type": "email"},
            {"name": "linkedin_field", "label": "LinkedIn URL", "type": "text"},
            {"name": "phone_field", "label": "Phone Number", "type": "tel"},
            {"name": "essay_field", "label": "Why do you want this role?", "type": "textarea"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["email_field"] == "email"
    assert mappings["linkedin_field"] == "linkedin"
    assert mappings["phone_field"] == "phone"
    assert mappings["essay_field"] is None


@pytest.mark.asyncio
async def test_keyword_fallback_covers_expanded_profile_taxonomy() -> None:
    state = {
        "extracted_fields": [
            {"name": "company", "label": "Current Company", "type": "text"},
            {"name": "title", "label": "Current Job Title", "type": "text"},
            {"name": "school", "label": "University", "type": "text"},
            {"name": "relocate", "label": "Willing to Relocate?", "type": "text"},
            {"name": "start", "label": "Earliest Start Date", "type": "text"},
            {"name": "expected", "label": "Expected Salary", "type": "text"},
            {"name": "current_comp", "label": "Current CTC", "type": "text"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["company"] == "current_company"
    assert mappings["title"] == "current_job_title"
    assert mappings["school"] == "university"
    assert mappings["relocate"] == "willing_to_relocate"
    assert mappings["start"] == "availability"
    assert mappings["expected"] == "salary"
    assert mappings["current_comp"] == "current_salary"


@pytest.mark.asyncio
async def test_keyword_fallback_disambiguates_specific_from_broad_fields() -> None:
    """Regression guard: adding specific canonical keys (city, degree,
    work_authorized, ...) must not get shadowed by the broader existing
    entries they overlap with (location, highest_education, visa_status)."""
    state = {
        "extracted_fields": [
            {"name": "city", "label": "City", "type": "text"},
            {"name": "addr", "label": "Current Location", "type": "text"},
            {"name": "deg", "label": "Degree", "type": "text"},
            {"name": "qual", "label": "Highest Qualification", "type": "text"},
            {"name": "auth", "label": "Are you legally authorized to work in this country?", "type": "text"},
            {"name": "visa", "label": "Visa Status", "type": "text"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["city"] == "city"
    assert mappings["addr"] == "location"
    assert mappings["deg"] == "degree"
    assert mappings["qual"] == "highest_education"
    assert mappings["auth"] == "work_authorized"
    assert mappings["visa"] == "visa_status"


@pytest.mark.asyncio
async def test_keyword_fallback_matches_bare_job_title_and_company() -> None:
    """Regression test for a real production incident: a Workday-style form
    asked plain "Job Title*" / "Company*" (not "Current Job Title"), which
    fell through unmatched because the keyword patterns only recognized the
    "current ..." phrasing."""
    state = {
        "extracted_fields": [
            {"name": "jobTitle", "label": "Job Title*", "type": "text"},
            {"name": "companyName", "label": "Company*", "type": "text"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["jobTitle"] == "current_job_title"
    assert mappings["companyName"] == "current_company"


@pytest.mark.asyncio
async def test_keyword_fallback_matches_camelcase_field_names_used_as_labels() -> None:
    """When a field has no real <label>/aria-label (common in JS-heavy ATS
    UIs), extraction falls back to the raw attribute name (e.g. "jobTitle")
    as the label — camelCase-splitting must let this still match, without
    breaking genuine words that happen to contain capitals mid-word (e.g.
    "LinkedIn" must not become "Linked In")."""
    state = {
        "extracted_fields": [
            {"name": "jobTitle", "label": None, "type": "text"},
            {"name": "linkedinUrl", "label": None, "type": "text"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["jobTitle"] == "current_job_title"
    assert mappings["linkedinUrl"] == "linkedin"


@pytest.mark.asyncio
async def test_keyword_fallback_matches_bare_name_field() -> None:
    """Regression test for a real production incident: a form field simply
    labeled "Name" was left unmapped and unfilled — the "name" canonical key
    previously only matched multi-word phrasings ("Full Name", "Your Name",
    "Candidate Name"), never the bare word by itself."""
    state = {
        "extracted_fields": [
            {"name": "name_field", "label": "Name", "type": "text"},
            {"name": "name_field_star", "label": "Name *", "type": "text"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["name_field"] == "name"
    assert mappings["name_field_star"] == "name"


@pytest.mark.asyncio
async def test_bare_name_fallback_does_not_shadow_more_specific_name_fields() -> None:
    """Regression guard: the bare "Name" fallback is checked last precisely
    so it can't hijack "Company Name" / "School Name" / "Employer Name",
    which must keep resolving to their own more specific canonical keys."""
    state = {
        "extracted_fields": [
            {"name": "company", "label": "Company Name", "type": "text"},
            {"name": "school", "label": "School Name", "type": "text"},
        ]
    }
    result = await semantic_matching_node(state, EmbeddingUnavailableLLM())
    mappings = result["field_mappings"]

    assert mappings["company"] == "current_company"
    assert mappings["school"] == "university"
