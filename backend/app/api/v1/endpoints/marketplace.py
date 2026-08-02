"""Lumini agent marketplace: browse agents and chat with them."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.registry import get_agent, list_agents
from app.core.exceptions import NotFoundError
from app.core.security import get_current_user
from app.db.session import get_db
from app.llm.client import LLMClient, get_llm_client
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.marketplace import (
    AgentCard,
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationRead,
    MessageRead,
)
from app.services.agent_chat_service import AgentChatService
from app.services.image_generation_service import is_configured as image_is_configured

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _card(spec) -> AgentCard:
    """Builds the listing, resolving any status that depends on runtime
    configuration rather than the static registry."""
    card = AgentCard(**vars(spec))
    if spec.slug == "image" and image_is_configured():
        card.status = "live"
        card.setup_hint = None
    return card


@router.get("/agents", response_model=List[AgentCard])
async def browse_agents() -> List[AgentCard]:
    """The marketplace catalog. Public-shaped data, but still auth-free so the
    grid can render before the user has a session."""
    return [_card(spec) for spec in list_agents()]


@router.get("/agents/{slug}", response_model=AgentCard)
async def get_agent_detail(slug: str) -> AgentCard:
    spec = get_agent(slug)
    if spec is None:
        raise NotFoundError(f"No agent named '{slug}'")
    return _card(spec)


@router.get("/agents/{slug}/conversations", response_model=List[ConversationRead])
async def list_conversations(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ConversationRead]:
    if get_agent(slug) is None:
        raise NotFoundError(f"No agent named '{slug}'")
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id, Conversation.agent_slug == slug)
        .order_by(Conversation.updated_at.desc())
    )
    return [ConversationRead.model_validate(c) for c in result.scalars().all()]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    conversation = await _owned_conversation(db, conversation_id, current_user)
    return ConversationDetail(
        id=conversation.id,
        agent_slug=conversation.agent_slug,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageRead(id=m.id, role=m.role.value, content=m.content, created_at=m.created_at)
            for m in conversation.messages
        ],
    )


@router.delete("/conversations/{conversation_id}", status_code=204, response_model=None)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    conversation = await _owned_conversation(db, conversation_id, current_user)
    await db.delete(conversation)


@router.post("/agents/{slug}/chat", response_model=ChatResponse)
async def chat_with_agent(
    slug: str,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> ChatResponse:
    spec = get_agent(slug)
    if spec is None:
        raise NotFoundError(f"No agent named '{slug}'")

    if payload.conversation_id is not None:
        conversation = await _owned_conversation(db, payload.conversation_id, current_user)
    else:
        conversation = Conversation(user_id=current_user.id, agent_slug=slug, title="New chat")
        db.add(conversation)
        await db.flush()

    service = AgentChatService(db, llm_client)
    if slug == "image":
        # For the image agent every message is a generation prompt, not a
        # question — routing it through the chat LLM would just describe an
        # image instead of producing one.
        reply = await service.send_image_prompt(
            conversation=conversation, prompt=payload.message, user_id=current_user.id
        )
    else:
        reply = await service.send(
            agent=spec, conversation=conversation, user_message=payload.message
        )

    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageRead(
            id=reply.id, role=reply.role.value, content=reply.content, created_at=reply.created_at
        ),
    )


async def _owned_conversation(
    db: AsyncSession, conversation_id: uuid.UUID, user: User
) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    # Same 404 for "doesn't exist" and "belongs to someone else" — a
    # distinct 403 would confirm the ID is real to a probing caller.
    if conversation is None or conversation.user_id != user.id:
        raise NotFoundError("Conversation not found")
    return conversation
