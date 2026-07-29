"""Expand profiles with additional job-application fields: identity
(full_name, headline, summary), more links (twitter), current role/education
(current_company, current_job_title, highest_education, university,
graduation_year), preferences (willing_to_relocate, remote_preference,
availability, cover_letter, current_salary), and list fields
(languages_spoken, certifications).

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-28
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("full_name", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("headline", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("twitter_url", sa.String(500), nullable=True))
    op.add_column("profiles", sa.Column("current_company", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("current_job_title", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("highest_education", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("university", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("graduation_year", sa.Integer(), nullable=True))
    # Note: current_salary already exists from 0001 (an original field).
    op.add_column("profiles", sa.Column("willing_to_relocate", sa.Boolean(), nullable=True))
    op.add_column("profiles", sa.Column("remote_preference", sa.String(100), nullable=True))
    op.add_column("profiles", sa.Column("availability", sa.String(255), nullable=True))
    op.add_column("profiles", sa.Column("cover_letter", sa.Text(), nullable=True))
    op.add_column(
        "profiles", sa.Column("languages_spoken", sa.JSON(), nullable=False, server_default="[]")
    )
    op.add_column(
        "profiles", sa.Column("certifications", sa.JSON(), nullable=False, server_default="[]")
    )


def downgrade() -> None:
    op.drop_column("profiles", "certifications")
    op.drop_column("profiles", "languages_spoken")
    op.drop_column("profiles", "cover_letter")
    op.drop_column("profiles", "availability")
    op.drop_column("profiles", "remote_preference")
    op.drop_column("profiles", "willing_to_relocate")
    op.drop_column("profiles", "current_salary")
    op.drop_column("profiles", "graduation_year")
    op.drop_column("profiles", "university")
    op.drop_column("profiles", "highest_education")
    op.drop_column("profiles", "current_job_title")
    op.drop_column("profiles", "current_company")
    op.drop_column("profiles", "twitter_url")
    op.drop_column("profiles", "summary")
    op.drop_column("profiles", "headline")
    op.drop_column("profiles", "full_name")
