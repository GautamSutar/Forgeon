"""Shared pytest fixtures.

Tests run against an in-memory SQLite database (via aiosqlite) rather than a
live Postgres instance, so the suite is self-contained. This is a documented
tradeoff: pgvector-specific operators (cosine_distance) are not available
under SQLite, so any test that exercises real vector search mocks
RetrieverService instead. For a true end-to-end pgvector test, point
DATABASE_URL at a live pgvector/pgvector:pg16 Postgres instance and re-run.

The real LLM client (`app.llm.client.LLMClient`) is monkeypatched everywhere
so tests never hit a real API.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, AsyncGenerator, Dict, List

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401 ensure models are registered
from app.db.session import get_db
from app.llm.client import LLMClient
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from app.llm.client import get_llm_client

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient()

    from langgraph.checkpoint.memory import MemorySaver

    app.state.checkpointer = MemorySaver()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


class FakeLLMClient(LLMClient):
    """Deterministic stand-in for LLMClient — never calls a real API."""

    def __init__(self, chat_response: str = "OK", structured_responses: List[Any] | None = None) -> None:
        super().__init__(model="fake-model", api_key="fake-key")
        self.chat_response = chat_response
        self._structured_queue = list(structured_responses or [])
        self.chat_calls: List[Any] = []
        self.structured_calls: List[Any] = []
        self.embed_calls: List[Any] = []

    async def chat(self, messages, *, model=None, max_tokens=2048, temperature=0.2, **kwargs) -> str:  # type: ignore[override]
        self.chat_calls.append(messages)
        return self.chat_response

    async def structured_chat(self, messages, output_model, *, model=None, max_tokens=2048, temperature=0.0, **kwargs):  # type: ignore[override]
        self.structured_calls.append((messages, output_model))
        if self._structured_queue:
            preset = self._structured_queue.pop(0)
            if isinstance(preset, output_model):
                return preset
            return output_model.model_validate(preset)
        # Best-effort empty-ish default instance. Uses model_validate({}) rather
        # than model_construct() so that Pydantic field defaults are actually
        # applied — model_construct() leaves fields with no explicit value
        # entirely unset, which raises AttributeError on access.
        return output_model.model_validate({})

    async def embed(self, texts, *, model=None) -> List[List[float]]:  # type: ignore[override]
        self.embed_calls.append(texts)
        # Deterministic pseudo-embeddings based on text hash, matching the
        # real EMBEDDING_DIMENSIONS so pgvector's fixed-width column accepts
        # them (SQLite doesn't enforce this, but Postgres/pgvector does).
        return [_pseudo_embedding(t) for t in texts]


def _pseudo_embedding(text: str, dim: int = settings.EMBEDDING_DIMENSIONS) -> List[float]:
    seed = sum(ord(c) for c in text) or 1
    return [((seed * (i + 1)) % 97) / 97.0 for i in range(dim)]


@pytest.fixture
def fake_llm_client() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
