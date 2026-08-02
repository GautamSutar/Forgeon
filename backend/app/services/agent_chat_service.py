"""Conversational runtime for marketplace agents.

Each agent is a system prompt plus a persisted message history. The agent's
own `system_prompt` carries its role and its honest limits (no live web, no
device attached, etc.) so refusals come from the agent's own framing rather
than being bolted on afterwards.
"""
from __future__ import annotations

import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import AgentSpec
from app.llm.client import LLMClient
from app.models.conversation import Conversation, Message, MessageRole
from app.services.image_generation_service import ImageGenerationError, ImageGenerationService

logger = logging.getLogger("app.services.agent_chat")

# How many prior messages to replay as context. Keeps token use bounded on
# long conversations while preserving recent back-and-forth.
MAX_HISTORY_MESSAGES = 20


class AgentChatService:
    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self.db = db
        self.llm = llm_client

    async def _history(self, conversation_id) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def send(
        self, *, agent: AgentSpec, conversation: Conversation, user_message: str
    ) -> Message:
        """Persists the user's message, generates a reply, persists it too."""
        history = await self._history(conversation.id)

        self.db.add(
            Message(conversation_id=conversation.id, role=MessageRole.USER, content=user_message)
        )
        await self.db.flush()

        prompt: List[dict] = [{"role": "system", "content": agent.system_prompt}]
        for m in history[-MAX_HISTORY_MESSAGES:]:
            prompt.append({"role": m.role.value, "content": m.content})
        prompt.append({"role": "user", "content": user_message})

        try:
            reply_text = await self.llm.chat(prompt, temperature=0.4)
        except Exception as exc:
            logger.warning("Agent %s chat failed: %s", agent.slug, exc)
            # Surfaced to the user as an assistant turn rather than a 500, so
            # the conversation stays coherent and the failure is visible in
            # the transcript instead of vanishing.
            reply_text = (
                "I couldn't reach the language model just now, so I can't answer "
                "this turn. Check that an LLM provider key is configured in "
                "backend/.env, then try again."
            )

        reply = Message(
            conversation_id=conversation.id, role=MessageRole.ASSISTANT, content=reply_text
        )
        self.db.add(reply)

        # First real exchange names the thread, so the sidebar isn't a wall
        # of "New chat".
        if conversation.title == "New chat":
            conversation.title = user_message[:60] + ("…" if len(user_message) > 60 else "")

        await self.db.flush()
        return reply

    async def send_image_prompt(
        self, *, conversation: Conversation, prompt: str, user_id
    ) -> Message:
        """Image-agent turn: the message *is* the prompt, and the reply is the
        rendered image.

        The result is stored as markdown so it round-trips through the normal
        conversation history and renders with the same pipeline as any other
        reply — no separate attachment table or column needed.
        """
        self.db.add(
            Message(conversation_id=conversation.id, role=MessageRole.USER, content=prompt)
        )
        await self.db.flush()

        service = ImageGenerationService()
        try:
            image = await service.generate(prompt, user_id=user_id)
            content = f"![{prompt}]({image.url})"
        except ImageGenerationError as exc:
            # Surfaced as an assistant turn, so the failure stays visible in
            # the transcript instead of vanishing into a toast.
            content = str(exc)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Unexpected image generation failure: %s", exc)
            content = "Image generation failed unexpectedly. Check the backend logs."

        reply = Message(
            conversation_id=conversation.id, role=MessageRole.ASSISTANT, content=content
        )
        self.db.add(reply)

        if conversation.title == "New chat":
            conversation.title = prompt[:60] + ("…" if len(prompt) > 60 else "")

        await self.db.flush()
        return reply
