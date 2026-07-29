from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.application import Application


class QuestionType(str, enum.Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"


class AnswerSource(str, enum.Enum):
    PROFILE = "profile"
    GENERATED = "generated"
    SAVED_ANSWER = "saved_answer"


class ApplicationAnswer(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "application_answers"

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_label: Mapped[str] = mapped_column(String(500), nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, name="question_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    generated_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    was_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source: Mapped[AnswerSource] = mapped_column(
        Enum(AnswerSource, name="answer_source", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    application: Mapped["Application"] = relationship(back_populates="answers")
