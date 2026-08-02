from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AgentCard(BaseModel):
    """An agent as shown in the marketplace grid."""

    slug: str
    name: str
    tagline: str
    description: str
    category: str
    icon: str
    accent: str
    capabilities: List[str]
    example_prompts: List[str]
    status: str
    setup_hint: Optional[str] = None
    route: Optional[str] = None
    creator: str
    version: str
    rating: float
    installs: int
    tags: List[str]


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_slug: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationRead):
    messages: List[MessageRead] = []


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[uuid.UUID] = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message: MessageRead
