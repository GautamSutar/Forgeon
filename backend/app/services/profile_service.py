from __future__ import annotations

import uuid
from typing import Any, Dict

from app.core.exceptions import NotFoundError
from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository) -> None:
        self.profile_repo = profile_repo

    async def get_or_create(self, user_id: uuid.UUID, full_name: str | None = None) -> Profile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            profile = await self.profile_repo.create(user_id=user_id, full_name=full_name)
        return profile

    async def update(self, user_id: uuid.UUID, data: Dict[str, Any], full_name: str | None = None) -> Profile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            data = {**data, "user_id": user_id}
            data.setdefault("full_name", full_name)
            profile = await self.profile_repo.create(**{k: v for k, v in data.items() if v is not None})
            return profile
        return await self.profile_repo.update(profile, **data)

    async def get(self, user_id: uuid.UUID) -> Profile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundError("Profile not found")
        return profile
