from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.application_answer import ApplicationAnswer
    from app.models.user import User


class ApplicationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUBMITTED = "submitted"
    FAILED = "failed"


class Application(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    job_description_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id", ondelete="RESTRICT"), nullable=False)
    role_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", values_callable=lambda x: [e.value for e in x]),
        default=ApplicationStatus.DRAFT,
        nullable=False,
        index=True,
    )
    ats_platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    user: Mapped["User"] = relationship(back_populates="applications")
    answers: Mapped[List["ApplicationAnswer"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
