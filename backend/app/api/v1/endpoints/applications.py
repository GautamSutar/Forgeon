from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_application_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    app_ = await application_service.create(current_user.id, payload.model_dump())
    return ApplicationRead.model_validate(app_)


@router.get("", response_model=List[ApplicationRead])
async def list_applications(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> List[ApplicationRead]:
    apps = await application_service.list_for_user(current_user.id, offset=offset, limit=limit)
    return [ApplicationRead.model_validate(a) for a in apps]


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    app_ = await application_service.get_owned(current_user.id, application_id)
    return ApplicationRead.model_validate(app_)


@router.patch("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: uuid.UUID,
    payload: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    app_ = await application_service.update(
        current_user.id, application_id, payload.model_dump(exclude_unset=True)
    )
    return ApplicationRead.model_validate(app_)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
) -> None:
    await application_service.delete(current_user.id, application_id)
