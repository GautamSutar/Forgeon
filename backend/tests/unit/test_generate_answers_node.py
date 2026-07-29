from __future__ import annotations

import asyncio

import pytest

from app.agents.nodes.generate_answers import generate_answers_node
from app.services.answer_generation_service import AnswerGenerationService, GeneratedAnswer


class DelayedAnswerService(AnswerGenerationService):
    """Records concurrent-call high-water-mark to prove dynamic fields are
    generated in parallel, not one at a time — the original implementation
    awaited each field sequentially in a for-loop, which on a real
    application form with many dynamic fields took minutes end-to-end.
    """

    def __init__(self, delay: float = 0.05) -> None:
        self.delay = delay
        self.in_flight = 0
        self.max_in_flight = 0

    async def generate_answer(
        self, *, field_label, field_type, job_description, retrieved_context, profile_summary
    ) -> GeneratedAnswer:
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(self.delay)
        self.in_flight -= 1
        return GeneratedAnswer(answer=f"answer for {field_label}", refused=False, reasoning="")


@pytest.mark.asyncio
async def test_dynamic_fields_generate_concurrently() -> None:
    service = DelayedAnswerService()
    state = {
        "extracted_fields": [
            {"name": f"q{i}", "label": f"Question {i}", "type": "textarea"} for i in range(4)
        ],
        "field_mappings": {},
        "profile": {},
        "retrieved_context": [],
        "job_description": "",
    }

    start = asyncio.get_event_loop().time()
    result = await generate_answers_node(state, service)
    elapsed = asyncio.get_event_loop().time() - start

    assert len(result["generated_answers"]) == 4
    # Proves real concurrency: more than one call was in flight at once,
    # and wall-clock time is well under 4x the per-call delay (sequential
    # would take ~4 * delay).
    assert service.max_in_flight > 1
    assert elapsed < service.delay * 3


@pytest.mark.asyncio
async def test_file_fields_skip_llm_generation() -> None:
    """Regression test: a file upload field (e.g. "Attach your resume") was
    being sent through the grounded-answer LLM like a text question, which
    can only ever refuse — there's no text answer to a file upload. File
    fields must be short-circuited before any LLM call."""
    service = DelayedAnswerService()
    state = {
        "extracted_fields": [
            {"name": "resume", "label": "Resume", "type": "file"},
        ],
        "field_mappings": {},
        "profile": {},
        "retrieved_context": [],
        "job_description": "",
    }

    result = await generate_answers_node(state, service)

    assert result["generated_answers"]["resume"]["refused"] is False
    assert service.max_in_flight == 0  # no LLM call was made


@pytest.mark.asyncio
async def test_static_fields_pulled_from_profile_without_llm_call() -> None:
    service = DelayedAnswerService()
    state = {
        "extracted_fields": [
            {"name": "email_field", "label": "Email", "type": "email"},
        ],
        "field_mappings": {"email_field": "email"},
        "profile": {"email": "jane.doe@example.com"},
        "retrieved_context": [],
        "job_description": "",
    }

    result = await generate_answers_node(state, service)

    assert result["generated_answers"]["email_field"]["answer"] == "jane.doe@example.com"
    assert result["generated_answers"]["email_field"]["source"] == "profile"
    assert service.max_in_flight == 0  # no LLM call was made at all


@pytest.mark.asyncio
async def test_job_title_and_company_fall_back_to_work_experience_history() -> None:
    """Regression test for a real production incident: a candidate filled
    in the structured, repeatable Work Experience section on their Profile
    (job_title/company per entry) but never separately filled the older
    flat current_job_title/current_company fields — a plain "Job Title" /
    "Company" question on a real form was refusing instead of resolving
    from that history."""
    service = DelayedAnswerService()
    state = {
        "extracted_fields": [
            {"name": "jobTitle", "label": "Job Title", "type": "text"},
            {"name": "companyName", "label": "Company", "type": "text"},
        ],
        "field_mappings": {"jobTitle": "current_job_title", "companyName": "current_company"},
        "profile": {
            "current_job_title": None,
            "current_company": None,
            "work_experience": [
                {
                    "job_title": "Python Developer Intern",
                    "company": "Initech Solutions",
                    "is_current": False,
                    "end_year": 2025,
                },
                {
                    "job_title": "AI Intern",
                    "company": "Globex Analytics",
                    "is_current": True,
                    "end_year": 2026,
                },
            ],
        },
        "retrieved_context": [],
        "job_description": "",
    }

    result = await generate_answers_node(state, service)

    # Must prefer the entry marked "currently work here" over the other one,
    # even though the other one has a later-looking end_year field present.
    assert result["generated_answers"]["jobTitle"]["answer"] == "AI Intern"
    assert result["generated_answers"]["companyName"]["answer"] == "Globex Analytics"
    assert result["generated_answers"]["jobTitle"]["source"] == "profile"
    assert service.max_in_flight == 0  # resolved from profile, no LLM call


@pytest.mark.asyncio
async def test_university_and_degree_fall_back_to_education_history() -> None:
    service = DelayedAnswerService()
    state = {
        "extracted_fields": [
            {"name": "school", "label": "University", "type": "text"},
            {"name": "deg", "label": "Degree", "type": "text"},
        ],
        "field_mappings": {"school": "university", "deg": "degree"},
        "profile": {
            "university": None,
            "degree": None,
            "education_history": [
                {"school": "Pink Flower H.S. School", "degree": None, "end_year": 2022},
                {"school": "Example Institute of Technology", "degree": "B.Tech", "end_year": 2026},
            ],
        },
        "retrieved_context": [],
        "job_description": "",
    }

    result = await generate_answers_node(state, service)

    assert result["generated_answers"]["school"]["answer"] == "Example Institute of Technology"
    assert result["generated_answers"]["deg"]["answer"] == "B.Tech"
