"""Generates embeddings via LiteLLM and persists them via pgvector."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import LLMClient
from app.models.embedding import Embedding, EmbeddingSourceType


class EmbeddingService:
    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self.db = db
        self.llm_client = llm_client

    async def embed_and_store(
        self,
        *,
        user_id: uuid.UUID,
        source_type: EmbeddingSourceType,
        content_chunks: List[str],
        source_id: Optional[uuid.UUID] = None,
    ) -> List[Embedding]:
        """Embed a list of text chunks and persist each as an Embedding row."""
        if not content_chunks:
            return []

        vectors = await self.llm_client.embed(content_chunks)
        rows: List[Embedding] = []
        for chunk, vector in zip(content_chunks, vectors):
            row = Embedding(
                user_id=user_id,
                source_type=source_type,
                source_id=source_id,
                content=chunk,
                embedding=vector,
            )
            self.db.add(row)
            rows.append(row)
        await self.db.flush()
        return rows

    @staticmethod
    def chunk_text(text: str, *, max_chars: int = 800, overlap: int = 100) -> List[str]:
        """Simple sliding-window chunker for resume/profile text."""
        text = text.strip()
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            chunks.append(text[start:end].strip())
            if end == len(text):
                break
            start = end - overlap
        return [c for c in chunks if c]
