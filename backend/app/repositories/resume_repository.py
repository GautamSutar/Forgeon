from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Resume)

    async def list_by_user(self, user_id: uuid.UUID) -> List[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_default(self, user_id: uuid.UUID) -> Optional[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id, Resume.is_default.is_(True))
        )
        return result.scalar_one_or_none()

    async def clear_default(self, user_id: uuid.UUID) -> None:
        resumes = await self.list_by_user(user_id)
        for r in resumes:
            if r.is_default:
                r.is_default = False
        await self.db.flush()
