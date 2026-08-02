from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    html: str
    job_description: str
    resume_id: Optional[uuid.UUID] = None
    # Detected client-side by the browser extension (content/detect.ts) —
    # optional because server-side/API-only callers won't have a page to
    # detect these from.
    ats_platform: Optional[str] = None
    source_url: Optional[str] = None


class AgentRunResponse(BaseModel):
    run_id: str
    status: str  # "interrupted" | "completed"
    preview: Optional[Dict[str, Any]] = None
    application_id: Optional[str] = None
    application_status: Optional[str] = None


class AgentApprovalRequest(BaseModel):
    edited_answers: Dict[str, str] = {}


class AgentRejectRequest(BaseModel):
    reason: Optional[str] = None
