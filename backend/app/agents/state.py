"""LangGraph agent state definition."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    run_id: str
    user_id: str
    application_id: Optional[str]

    # Inputs
    profile: Dict[str, Any]
    resume: Dict[str, Any]
    html: str
    job_description: str

    # Working data
    extracted_fields: List[Dict[str, Any]]
    jd_extracted: Dict[str, Any]
    retrieved_context: List[str]
    field_mappings: Dict[str, Optional[str]]
    generated_answers: Dict[str, Dict[str, Any]]
    filled_fields: Dict[str, str]

    # Validation / approval / submission
    validation_errors: List[str]
    retry_count: int
    approval_status: str  # "pending" | "approved" | "rejected" | "edited"
    approved_answers: Dict[str, str]
    application_status: str  # "draft" | "pending_approval" | "approved" | "rejected" | "submitted" | "failed"

    errors: List[str]
