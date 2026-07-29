from __future__ import annotations

import enum
import uuid
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.db.base import Base, TimestampMixin, UUIDPKMixin


class EmbeddingSourceType(str, enum.Enum):
    RESUME_CHUNK = "resume_chunk"
    PROJECT = "project"
    SKILL = "skill"
    SAVED_ANSWER = "saved_answer"
    INTERVIEW_ANSWER = "interview_answer"
    COMPANY_NOTE = "company_note"


class Embedding(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "embeddings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type: Mapped[EmbeddingSourceType] = mapped_column(
        Enum(
            EmbeddingSourceType,
            name="embedding_source_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSIONS), nullable=False
    )
