"""Node: persist Application + ApplicationAnswer rows for this run."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.models.application import Application, ApplicationStatus
from app.models.application_answer import AnswerSource, ApplicationAnswer, QuestionType

logger = logging.getLogger("app.agents.save_history")

_STATUS_MAP = {
    "submitted": ApplicationStatus.SUBMITTED,
    "approved": ApplicationStatus.APPROVED,
    "rejected": ApplicationStatus.REJECTED,
    "failed": ApplicationStatus.FAILED,
}


async def save_history_node(state: AgentState, db: AsyncSession) -> Dict[str, Any]:
    user_id_raw = state.get("user_id")
    if not user_id_raw:
        return {}

    user_id = uuid.UUID(user_id_raw)
    resume = state.get("resume", {})
    resume_id_raw = resume.get("id")

    application_status_key = state.get("application_status") or (
        "rejected" if state.get("approval_status") == "rejected" else "pending_approval"
    )
    status = _STATUS_MAP.get(application_status_key, ApplicationStatus.PENDING_APPROVAL)

    application: Application | None = None
    if resume_id_raw:
        application = Application(
            user_id=user_id,
            resume_id=uuid.UUID(resume_id_raw),
            role_title=state.get("jd_extracted", {}).get("role_title"),
            status=status,
        )
        db.add(application)
        await db.flush()

        answers = state.get("generated_answers", {})
        approved_answers = state.get("approved_answers", {})
        fields = {f.get("name") or f.get("label"): f for f in state.get("extracted_fields", [])}

        for field_key, entry in answers.items():
            field_meta = fields.get(field_key, {})
            db.add(
                ApplicationAnswer(
                    application_id=application.id,
                    field_label=field_meta.get("label") or field_key,
                    field_name=field_key,
                    canonical_key=entry.get("canonical_key"),
                    question_type=QuestionType.STATIC if entry.get("source") == "profile" else QuestionType.DYNAMIC,
                    generated_answer=entry.get("answer"),
                    final_answer=approved_answers.get(field_key, entry.get("answer")),
                    was_edited=bool(entry.get("was_edited", False)),
                    source=AnswerSource(entry.get("source", "generated")),
                )
            )
        await db.flush()

    return {"application_id": str(application.id) if application else None}


def make_save_history_node(db: AsyncSession):
    async def _node(state: AgentState) -> Dict[str, Any]:
        return await save_history_node(state, db)

    return _node
