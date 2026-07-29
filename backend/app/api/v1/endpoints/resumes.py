from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, status

from app.api.deps import get_resume_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeRead, ResumeUploadResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    set_default: bool = False,
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeUploadResponse:
    file_bytes = await file.read()
    resume = await resume_service.upload(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        file_bytes=file_bytes,
        set_default=set_default,
    )
    resume = await resume_service.parse_and_embed(resume)
    return ResumeUploadResponse.model_validate(resume)


@router.get("", response_model=List[ResumeRead])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> List[ResumeRead]:
    resumes = await resume_service.list_for_user(current_user.id)
    return [ResumeRead.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeRead)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeRead:
    resume = await resume_service.get_owned(current_user.id, resume_id)
    return ResumeRead.model_validate(resume)


@router.post("/{resume_id}/set-default", response_model=ResumeRead)
async def set_default_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeRead:
    resume = await resume_service.set_default(current_user.id, resume_id)
    return ResumeRead.model_validate(resume)


@router.post("/{resume_id}/parse", response_model=ResumeRead)
async def trigger_parse(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeRead:
    resume = await resume_service.get_owned(current_user.id, resume_id)
    resume = await resume_service.parse_and_embed(resume)
    return ResumeRead.model_validate(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> None:
    await resume_service.delete(current_user.id, resume_id)
