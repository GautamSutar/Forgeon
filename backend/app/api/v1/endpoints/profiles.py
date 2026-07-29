from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_profile_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileRead)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    profile = await profile_service.get_or_create(current_user.id, full_name=current_user.full_name)
    return ProfileRead.model_validate(profile)


@router.put("/me", response_model=ProfileRead)
async def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    profile = await profile_service.update(
        current_user.id, payload.model_dump(exclude_unset=True), full_name=current_user.full_name
    )
    return ProfileRead.model_validate(profile)
