from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Application)

    async def list_by_user(self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> List[Application]:
        result = await self.db.execute(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
