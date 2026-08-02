"""Agent endpoints: run the LangGraph job-application graph and handle
human-in-the-loop approve/reject of a paused (interrupted) run.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_answer_generation_service, get_retriever_service
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import get_current_user
from app.db.session import get_db
from app.agents.graph import build_graph
from app.llm.client import LLMClient, get_llm_client
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.agent import (
    AgentApprovalRequest,
    AgentRejectRequest,
    AgentRunRequest,
    AgentRunResponse,
)
from app.schemas.profile import ProfileRead
from app.schemas.resume import ResumeRead
from app.services.answer_generation_service import AnswerGenerationService
from app.services.retriever_service import RetrieverService

router = APIRouter(prefix="/agent", tags=["agent"])


def _get_checkpointer(request: Request):
    return request.app.state.checkpointer


async def _build_state(
    db: AsyncSession,
    current_user: User,
    payload: AgentRunRequest,
) -> Dict[str, Any]:
    profile_repo = ProfileRepository(db)
    resume_repo = ResumeRepository(db)

    profile = await profile_repo.get_by_user_id(current_user.id)
    if payload.resume_id:
        resume = await resume_repo.get(payload.resume_id)
        if resume is None or resume.user_id != current_user.id:
            raise NotFoundError("Resume not found")
    else:
        resume = await resume_repo.get_default(current_user.id)
        if resume is None:
            raise ValidationAppError("No default resume set. Upload and set a default resume first.")

    profile_dict = ProfileRead.model_validate(profile).model_dump(mode="json") if profile else {}
    # Name/email are guaranteed to be answerable from the account itself,
    # regardless of whether the candidate has ever opened the Profile page —
    # full_name only overlays if the profile didn't already have one set
    # (e.g. edited to a preferred display name), email always comes from the
    # account since it's not a separately editable Profile field.
    profile_dict.setdefault("full_name", current_user.full_name)
    profile_dict["email"] = current_user.email
    resume_dict = ResumeRead.model_validate(resume).model_dump(mode="json")

    return {
        "run_id": "",  # set by caller
        "user_id": str(current_user.id),
        "profile": profile_dict,
        "resume": resume_dict,
        "html": payload.html,
        "job_description": payload.job_description,
        "ats_platform": payload.ats_platform,
        "source_url": payload.source_url,
        "extracted_fields": [],
        "generated_answers": {},
        "retry_count": 0,
        "errors": [],
        "approval_status": "pending",
    }


async def _extract_preview(graph, config: Dict[str, Any]) -> Dict[str, Any] | None:
    """Reads pending interrupts off the graph's checkpointed state.

    Note: this LangGraph version does not surface interrupts via a
    `__interrupt__` key on the `ainvoke()` result dict — they only appear on
    the state snapshot's pending tasks, so we must check `aget_state()`
    after every invoke/resume to know whether the run paused.
    """
    snapshot = await graph.aget_state(config)
    for task in snapshot.tasks:
        if task.interrupts:
            value = task.interrupts[0].value
            return value if isinstance(value, dict) else {"data": value}
    return None


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    payload: AgentRunRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    retriever_service: RetrieverService = Depends(get_retriever_service),
    answer_service: AnswerGenerationService = Depends(get_answer_generation_service),
) -> AgentRunResponse:
    run_id = str(uuid.uuid4())
    checkpointer = _get_checkpointer(request)

    graph = build_graph(
        llm_client=llm_client,
        retriever_service=retriever_service,
        answer_service=answer_service,
        db_session=db,
        playwright_tool=None,
        checkpointer=checkpointer,
    )

    state = await _build_state(db, current_user, payload)
    state["run_id"] = run_id

    config = {"configurable": {"thread_id": run_id}}
    result = await graph.ainvoke(state, config=config)
    await db.commit()

    preview = await _extract_preview(graph, config)
    if preview is not None:
        return AgentRunResponse(run_id=run_id, status="interrupted", preview=preview)

    return AgentRunResponse(
        run_id=run_id,
        status="completed",
        application_id=result.get("application_id"),
        application_status=result.get("application_status"),
    )


@router.post("/{run_id}/approve", response_model=AgentRunResponse)
async def approve_run(
    run_id: str,
    payload: AgentApprovalRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    retriever_service: RetrieverService = Depends(get_retriever_service),
    answer_service: AnswerGenerationService = Depends(get_answer_generation_service),
) -> AgentRunResponse:
    checkpointer = _get_checkpointer(request)
    graph = build_graph(
        llm_client=llm_client,
        retriever_service=retriever_service,
        answer_service=answer_service,
        db_session=db,
        playwright_tool=None,
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": run_id}}
    resume_value = {"approval_status": "approved", "edited_answers": payload.edited_answers}
    result = await graph.ainvoke(Command(resume=resume_value), config=config)
    await db.commit()

    preview = await _extract_preview(graph, config)
    if preview is not None:
        return AgentRunResponse(run_id=run_id, status="interrupted", preview=preview)

    return AgentRunResponse(
        run_id=run_id,
        status="completed",
        application_id=result.get("application_id"),
        application_status=result.get("application_status"),
    )


@router.post("/{run_id}/reject", response_model=AgentRunResponse)
async def reject_run(
    run_id: str,
    payload: AgentRejectRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    retriever_service: RetrieverService = Depends(get_retriever_service),
    answer_service: AnswerGenerationService = Depends(get_answer_generation_service),
) -> AgentRunResponse:
    checkpointer = _get_checkpointer(request)
    graph = build_graph(
        llm_client=llm_client,
        retriever_service=retriever_service,
        answer_service=answer_service,
        db_session=db,
        playwright_tool=None,
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": run_id}}
    result = await graph.ainvoke(Command(resume={"approval_status": "rejected"}), config=config)
    await db.commit()

    return AgentRunResponse(
        run_id=run_id,
        status="completed",
        application_id=result.get("application_id"),
        application_status=result.get("application_status"),
    )
