"""Node: validate generated/filled answers — required fields, email format, non-empty."""
from __future__ import annotations

import re
from typing import Any, Dict

from app.agents.state import AgentState

EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

MAX_RETRIES = 2


async def validate_node(state: AgentState) -> Dict[str, Any]:
    fields = state.get("extracted_fields", [])
    answers = state.get("generated_answers", {})
    errors = []

    for field in fields:
        field_key = field.get("name") or field.get("label") or ""
        if not field_key:
            continue
        entry = answers.get(field_key)
        answer_text = (entry or {}).get("answer", "")

        if field.get("required") and not str(answer_text).strip():
            errors.append(f"Required field '{field.get('label') or field_key}' is empty")
            continue

        if field.get("type") == "email" and answer_text:
            if not EMAIL_RE.match(str(answer_text)):
                errors.append(f"Field '{field.get('label') or field_key}' has an invalid email format")

    retry_count = state.get("retry_count", 0)
    return {"validation_errors": errors, "retry_count": retry_count}


def route_after_validate(state: AgentState) -> str:
    """Conditional edge: retry generation (up to MAX_RETRIES) or proceed to approval."""
    errors = state.get("validation_errors", [])
    retry_count = state.get("retry_count", 0)

    if not errors:
        return "human_approval"
    if retry_count < MAX_RETRIES:
        return "retry"
    return "human_approval"  # give up retrying, surface errors for human review


async def increment_retry_node(state: AgentState) -> Dict[str, Any]:
    return {"retry_count": state.get("retry_count", 0) + 1}
