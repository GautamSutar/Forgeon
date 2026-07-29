"""Node: pause the graph for human-in-the-loop approval before submission.

Uses LangGraph's interrupt() primitive. When the graph is resumed (via
Command(resume=...)), the resumed value is read as the approval decision and
merged into state.
"""
from __future__ import annotations

from typing import Any, Dict

from langgraph.types import interrupt

from app.agents.state import AgentState


def build_preview_payload(state: AgentState) -> Dict[str, Any]:
    return {
        "run_id": state.get("run_id"),
        "fields": state.get("extracted_fields", []),
        "answers": state.get("generated_answers", {}),
        "validation_errors": state.get("validation_errors", []),
        "job_description": state.get("job_description", ""),
    }


async def human_approval_node(state: AgentState) -> Dict[str, Any]:
    preview = build_preview_payload(state)

    # This pauses graph execution. The caller resumes with
    # Command(resume={"approval_status": "approved"|"rejected"|"edited",
    #                  "edited_answers": {...}}).
    decision = interrupt(preview)

    if not isinstance(decision, dict):
        decision = {"approval_status": "rejected"}

    approval_status = decision.get("approval_status", "rejected")
    edited_answers = decision.get("edited_answers") or {}

    approved_answers = dict(state.get("generated_answers", {}))
    for key, value in edited_answers.items():
        if key in approved_answers:
            approved_answers[key] = {**approved_answers[key], "answer": value, "was_edited": True}

    return {
        "approval_status": approval_status,
        "approved_answers": {k: v.get("answer", "") for k, v in approved_answers.items()},
        "generated_answers": approved_answers,
    }


def route_after_approval(state: AgentState) -> str:
    status = state.get("approval_status")
    if status == "approved":
        return "submit"
    return "save_history"
