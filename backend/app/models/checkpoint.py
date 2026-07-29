"""App-level run-metadata table. LangGraph's own checkpointer manages its
internal checkpoint tables separately (created via langgraph's Postgres
checkpointer setup); this table tracks run -> user/application linkage and
high-level status for API-facing queries.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class AgentRun(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "checkpoints"

    run_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    thread_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="running", nullable=False)
