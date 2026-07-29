"""Builds grounded prompts and generates answers via the LLM, with an explicit
anti-hallucination system prompt. Refuses to fabricate when context is
insufficient.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.llm.client import LLMClient
from app.llm.prompts import answer_generation_prompt

REFUSAL_TEXT = "I don't have information to answer this accurately."


class GeneratedAnswer(BaseModel):
    answer: str
    refused: bool
    reasoning: str = ""


class AnswerGenerationService:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def generate_answer(
        self,
        *,
        field_label: str,
        field_type: str,
        job_description: str,
        retrieved_context: List[str],
        profile_summary: str,
    ) -> GeneratedAnswer:
        messages = answer_generation_prompt(
            field_label=field_label,
            field_type=field_type,
            job_description=job_description,
            retrieved_context=retrieved_context,
            profile_summary=profile_summary,
        )
        try:
            result = await self.llm_client.structured_chat(messages, GeneratedAnswer)
        except Exception:
            # If the model call or parsing fails, refuse rather than risk fabrication.
            return GeneratedAnswer(answer=REFUSAL_TEXT, refused=True, reasoning="LLM call or parsing failed")

        if not retrieved_context and not result.refused:
            # No grounding context was available at all — force a refusal regardless
            # of what the model produced, as a hard safety net.
            return GeneratedAnswer(
                answer=REFUSAL_TEXT,
                refused=True,
                reasoning="No retrieved context was available to ground this answer",
            )
        return result
