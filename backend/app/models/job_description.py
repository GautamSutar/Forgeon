from __future__ import annotations

import uuid
from typing import Any, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, PortableJSON, TimestampMixin, UUIDPKMixin


class JobDescription(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "job_descriptions"

    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    role_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    skills: Mapped[List[Any]] = mapped_column(PortableJSON, default=list)
    responsibilities: Mapped[List[Any]] = mapped_column(PortableJSON, default=list)
    requirements: Mapped[List[Any]] = mapped_column(PortableJSON, default=list)
    nice_to_have: Mapped[List[Any]] = mapped_column(PortableJSON, default=list)
    experience_required: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
