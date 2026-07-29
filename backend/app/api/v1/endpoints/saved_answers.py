from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_application_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.application import SavedAnswerCreate, SavedAnswerRead, SavedAnswerUpdate
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/saved-answers", tags=["saved-answers"])


@router.post("", response_model=SavedAnswerRead, status_code=status.HTTP_201_CREATED)
async def create_saved_answer(
    payload: SavedAnswerCreate,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> SavedAnswerRead:
    obj = await application_service.create_saved_answer(current_user.id, payload)
    return SavedAnswerRead.model_validate(obj)


@router.get("", response_model=List[SavedAnswerRead])
async def list_saved_answers(
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> List[SavedAnswerRead]:
    objs = await application_service.list_saved_answers(current_user.id)
    return [SavedAnswerRead.model_validate(o) for o in objs]


@router.get("/{saved_answer_id}", response_model=SavedAnswerRead)
async def get_saved_answer(
    saved_answer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> SavedAnswerRead:
    obj = await application_service.get_owned_saved_answer(current_user.id, saved_answer_id)
    return SavedAnswerRead.model_validate(obj)


@router.patch("/{saved_answer_id}", response_model=SavedAnswerRead)
async def update_saved_answer(
    saved_answer_id: uuid.UUID,
    payload: SavedAnswerUpdate,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> SavedAnswerRead:
    obj = await application_service.update_saved_answer(current_user.id, saved_answer_id, payload)
    return SavedAnswerRead.model_validate(obj)


@router.delete("/{saved_answer_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_saved_answer(
    saved_answer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> None:
    await application_service.delete_saved_answer(current_user.id, saved_answer_id)
