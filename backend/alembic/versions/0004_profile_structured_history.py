"""Add structured, repeatable history to profiles: work_experience and
education_history (Workday-style "Add Another" multi-entry sections, stored
as JSON lists of objects), plus a user-curated skills list (distinct from a
resume's raw parsed skills) and a generic websites list.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-28
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profiles", sa.Column("work_experience", sa.JSON(), nullable=False, server_default="[]")
    )
    op.add_column(
        "profiles", sa.Column("education_history", sa.JSON(), nullable=False, server_default="[]")
    )
    op.add_column("profiles", sa.Column("skills", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("profiles", sa.Column("websites", sa.JSON(), nullable=False, server_default="[]"))


def downgrade() -> None:
    op.drop_column("profiles", "websites")
    op.drop_column("profiles", "skills")
    op.drop_column("profiles", "education_history")
    op.drop_column("profiles", "work_experience")
