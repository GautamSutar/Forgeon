from __future__ import annotations

import uuid
from typing import Any, Dict, List

from app.core.exceptions import NotFoundError
from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.repositories.saved_answer_repository import SavedAnswerRepository
from app.schemas.application import SavedAnswerCreate, SavedAnswerUpdate


class ApplicationService:
    def __init__(self, application_repo: ApplicationRepository, saved_answer_repo: SavedAnswerRepository) -> None:
        self.application_repo = application_repo
        self.saved_answer_repo = saved_answer_repo

    async def create(self, user_id: uuid.UUID, data: Dict[str, Any]) -> Application:
        return await self.application_repo.create(user_id=user_id, **data)

    async def get_owned(self, user_id: uuid.UUID, application_id: uuid.UUID) -> Application:
        app_ = await self.application_repo.get(application_id)
        if app_ is None or app_.user_id != user_id:
            raise NotFoundError("Application not found")
        return app_

    async def list_for_user(self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> List[Application]:
        return await self.application_repo.list_by_user(user_id, offset=offset, limit=limit)

    async def update(self, user_id: uuid.UUID, application_id: uuid.UUID, data: Dict[str, Any]) -> Application:
        app_ = await self.get_owned(user_id, application_id)
        return await self.application_repo.update(app_, **data)

    async def delete(self, user_id: uuid.UUID, application_id: uuid.UUID) -> None:
        app_ = await self.get_owned(user_id, application_id)
        await self.application_repo.delete(app_)

    # Saved answers
    async def create_saved_answer(self, user_id: uuid.UUID, data: SavedAnswerCreate):
        return await self.saved_answer_repo.create(user_id=user_id, **data.model_dump())

    async def list_saved_answers(self, user_id: uuid.UUID):
        return await self.saved_answer_repo.list_by_user(user_id)

    async def get_owned_saved_answer(self, user_id: uuid.UUID, saved_answer_id: uuid.UUID):
        obj = await self.saved_answer_repo.get(saved_answer_id)
        if obj is None or obj.user_id != user_id:
            raise NotFoundError("Saved answer not found")
        return obj

    async def update_saved_answer(self, user_id: uuid.UUID, saved_answer_id: uuid.UUID, data: SavedAnswerUpdate):
        obj = await self.get_owned_saved_answer(user_id, saved_answer_id)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.saved_answer_repo.update(obj, **update_data)

    async def delete_saved_answer(self, user_id: uuid.UUID, saved_answer_id: uuid.UUID) -> None:
        obj = await self.get_owned_saved_answer(user_id, saved_answer_id)
        await self.saved_answer_repo.delete(obj)
