from __future__ import annotations

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class FieldAlias(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "field_aliases"

    canonical_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    alias_label: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
