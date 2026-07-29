"""Regression test for a critical bug: `get_db()` originally never committed
on success (only rolled back on exceptions). Every write in the app appeared
to succeed — the ORM object gets a PK from `flush()`, so a 201 response looks
fine — but a fresh per-request session's connection is released back to the
pool with an open, uncommitted transaction, which the database silently
rolls back. Nothing actually persisted across requests against real Postgres.

This slipped past the rest of the suite because the API test fixture
(tests/conftest.py) shares ONE session across an entire test via a
dependency override, so `flush()` alone was enough for later queries *in
that same session* to see the data. This test instead exercises `get_db()`
itself exactly as FastAPI would — open a session, write, let the generator
complete — then opens a genuinely separate session to verify the write
actually persisted.
"""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
import app.models  # noqa: F401 ensure models are registered
from app.db.session import get_db
from app.repositories.user_repository import UserRepository

pytestmark = pytest.mark.asyncio


async def test_get_db_commits_on_success() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    import app.db.session as db_session_module

    original_factory = db_session_module.AsyncSessionLocal
    db_session_module.AsyncSessionLocal = session_factory
    try:
        # Simulate exactly one FastAPI request: drive the get_db() generator
        # to completion without ever calling commit() ourselves.
        gen = get_db()
        session = await gen.__anext__()
        repo = UserRepository(session)
        await repo.create(email="persisted@test.com", hashed_password=hash_password("x"), full_name="Persisted User")
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()  # drives the generator's `finally` (and the commit before it)

        # A completely separate session must see the row if it was truly
        # committed — this is what real per-request traffic looks like.
        async with session_factory() as verify_session:
            verify_repo = UserRepository(verify_session)
            found = await verify_repo.get_by_email("persisted@test.com")
            assert found is not None
            assert found.email == "persisted@test.com"
    finally:
        db_session_module.AsyncSessionLocal = original_factory
        await engine.dispose()


async def test_get_db_rolls_back_on_exception() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    import app.db.session as db_session_module

    original_factory = db_session_module.AsyncSessionLocal
    db_session_module.AsyncSessionLocal = session_factory
    try:
        gen = get_db()
        session = await gen.__anext__()
        repo = UserRepository(session)
        await repo.create(email="rolledback@test.com", hashed_password=hash_password("x"), full_name="Rolled Back")

        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("simulated handler failure"))

        async with session_factory() as verify_session:
            verify_repo = UserRepository(verify_session)
            found = await verify_repo.get_by_email("rolledback@test.com")
            assert found is None
    finally:
        db_session_module.AsyncSessionLocal = original_factory
        await engine.dispose()
