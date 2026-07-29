"""Async SQLAlchemy engine, session factory, and get_db dependency."""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Per-request session. Commits automatically once the endpoint handler
    returns without raising — services/repositories only need to `flush()`
    to get PKs assigned, not `commit()` themselves. Without this, a fresh
    session's connection is released back to the pool at the end of the
    request with an open, uncommitted transaction, which Postgres silently
    rolls back — every write in the app would appear to succeed (the ORM
    object has an ID from the flush) but never actually persist.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
