"""RAG retrieval: cosine similarity search over embeddings, scoped by user."""
from __future__ import annotations

import uuid
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import LLMClient
from app.models.embedding import Embedding, EmbeddingSourceType


class RetrieverService:
    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self.db = db
        self.llm_client = llm_client

    async def retrieve(
        self,
        *,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5,
        source_types: Optional[Sequence[EmbeddingSourceType]] = None,
    ) -> List[Embedding]:
        """Embed the query and return top_k most similar Embedding rows for the user."""
        vectors = await self.llm_client.embed([query])
        query_vector = vectors[0]

        stmt = select(Embedding).where(Embedding.user_id == user_id)
        if source_types:
            stmt = stmt.where(Embedding.source_type.in_(source_types))
        stmt = stmt.order_by(Embedding.embedding.cosine_distance(query_vector)).limit(top_k)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def retrieve_text(
        self,
        *,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5,
        source_types: Optional[Sequence[EmbeddingSourceType]] = None,
    ) -> List[str]:
        rows = await self.retrieve(user_id=user_id, query=query, top_k=top_k, source_types=source_types)
        return [row.content for row in rows]
