from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, PortableJSON, TimestampMixin, UUIDPKMixin


class ApplicationLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "application_logs"

    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(PortableJSON, nullable=True)
