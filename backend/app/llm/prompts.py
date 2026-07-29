"""Prompt templates. Each function returns an OpenAI-style message list."""
from __future__ import annotations

import json
from typing import Any, Dict, List

Message = Dict[str, str]

ANTI_HALLUCINATION_SYSTEM_PROMPT = """You are an assistant that fills out job application forms on behalf of \
a real candidate. You operate under a strict grounding policy:

1. You may ONLY use facts that are explicitly present in the provided resume text, candidate profile, \
saved answers, or retrieved context passages. You must NEVER invent, infer, or embellish any company name, \
job title, date, metric, degree, certification, or accomplishment that is not directly present in the \
provided context.
2. If the provided context does not contain enough information to answer a question accurately, you MUST \
set "refused" to true and set "answer" to the exact string \
"I don't have information to answer this accurately." Do not guess.
3. Never fabricate specific numbers (e.g. "increased revenue by 30%") unless that exact figure appears in \
the provided context.
4. Prefer directly quoting or lightly paraphrasing the source material over generating novel prose.
5. You must always respond with valid JSON matching the requested schema. No markdown fences, no commentary \
outside the JSON object.
"""


def jd_extraction_prompt(jd_text: str) -> List[Message]:
    return [
        {
            "role": "system",
            "content": (
                "You are a precise information-extraction engine for job descriptions. Extract only what is "
                "explicitly stated in the text. Do not invent skills, requirements, or company details. "
                "Respond with JSON only."
            ),
        },
        {
            "role": "user",
            "content": f"Extract structured fields from this job description:\n\n{jd_text}",
        },
    ]


def semantic_field_mapping_prompt(field_label: str, canonical_keys: List[str]) -> List[Message]:
    return [
        {
            "role": "system",
            "content": (
                "You map a job application form field's label to the single best-matching canonical profile "
                "key from a fixed list, or null if none apply. Respond with JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Form field label: {field_label!r}\n"
                f"Canonical keys: {json.dumps(canonical_keys)}\n"
                "Which canonical key best matches this field label? If none is a good match, use null."
            ),
        },
    ]


def answer_generation_prompt(
    field_label: str,
    field_type: str,
    job_description: str,
    retrieved_context: List[str],
    profile_summary: str,
) -> List[Message]:
    context_block = "\n---\n".join(retrieved_context) if retrieved_context else "(no relevant context retrieved)"
    return [
        {"role": "system", "content": ANTI_HALLUCINATION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Job description (for context, do not copy verbatim unless relevant):\n{job_description}\n\n"
                f"Candidate profile summary:\n{profile_summary}\n\n"
                f"Retrieved grounding context (resume chunks, saved answers, etc.):\n{context_block}\n\n"
                f"Form field to answer:\nLabel: {field_label}\nType: {field_type}\n\n"
                "Generate a grounded, concise answer to this field using ONLY the information above. "
                "Respond with JSON: {\"answer\": string, \"refused\": boolean, \"reasoning\": string}."
            ),
        },
    ]


def resume_section_hint_prompt(raw_text: str) -> List[Message]:
    """Used only as a fallback hint generator; primary parsing is heuristic/regex-based."""
    return [
        {
            "role": "system",
            "content": (
                "You segment resume text into section boundaries only (skills, experience, education, "
                "projects, certifications, contact, links). Do not summarize or invent content."
            ),
        },
        {"role": "user", "content": raw_text},
    ]
