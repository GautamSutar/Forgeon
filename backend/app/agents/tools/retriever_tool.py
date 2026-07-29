"""Thin wrapper exposing RetrieverService for LLM tool-calling contexts."""
from __future__ import annotations

import uuid
from typing import List

from app.services.retriever_service import RetrieverService


class RetrieverTool:
    def __init__(self, retriever_service: RetrieverService) -> None:
        self.retriever_service = retriever_service

    async def search(self, user_id: str, query: str, top_k: int = 5) -> List[str]:
        return await self.retriever_service.retrieve_text(user_id=uuid.UUID(user_id), query=query, top_k=top_k)
