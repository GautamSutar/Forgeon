from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_answer import SavedAnswer
from app.repositories.base import BaseRepository


class SavedAnswerRepository(BaseRepository[SavedAnswer]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, SavedAnswer)

    async def list_by_user(self, user_id: uuid.UUID) -> List[SavedAnswer]:
        result = await self.db.execute(
            select(SavedAnswer).where(SavedAnswer.user_id == user_id).order_by(SavedAnswer.created_at.desc())
        )
        return list(result.scalars().all())
