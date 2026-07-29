from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.application import ApplicationStatus
from app.models.application_answer import AnswerSource, QuestionType


class ApplicationCreate(BaseModel):
    resume_id: uuid.UUID
    company_id: Optional[uuid.UUID] = None
    job_description_id: Optional[uuid.UUID] = None
    role_title: Optional[str] = None
    ats_platform: Optional[str] = None
    source_url: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    role_title: Optional[str] = None
    screenshot_path: Optional[str] = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    company_id: Optional[uuid.UUID]
    job_description_id: Optional[uuid.UUID]
    resume_id: uuid.UUID
    role_title: Optional[str]
    status: ApplicationStatus
    ats_platform: Optional[str]
    source_url: Optional[str]
    screenshot_path: Optional[str]
    created_at: datetime
    updated_at: datetime


class ApplicationAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    field_label: str
    field_name: str
    canonical_key: Optional[str]
    question_type: QuestionType
    generated_answer: Optional[str]
    final_answer: Optional[str]
    was_edited: bool
    source: AnswerSource


class SavedAnswerCreate(BaseModel):
    canonical_key: Optional[str] = None
    question_text: str
    answer_text: str


class SavedAnswerUpdate(BaseModel):
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    canonical_key: Optional[str] = None


class SavedAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    canonical_key: Optional[str]
    question_text: str
    answer_text: str
    usage_count: int
    created_at: datetime
    updated_at: datetime
