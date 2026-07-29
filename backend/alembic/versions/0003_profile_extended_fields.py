"""Extend profiles with a broad set of common job-application fields:
personal info (names, gender, DOB, nationality, marital status), structured
address, employment type preference, more social/community profile links
(Kaggle, LeetCode, HackerRank, CodeChef, GeeksforGeeks, StackOverflow,
Medium), education detail (degree, specialization, CGPA/percentages),
experience detail (fresher flag, relevant experience, reason for leaving),
work authorization (authorized flag, sponsorship, passport, citizenship),
voluntary diversity self-identification, availability (immediate joiner,
time zone), and additional list fields (awards, publications, hobbies).

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-28
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

_STRING_COLUMNS = [
    ("first_name", 100),
    ("middle_name", 100),
    ("last_name", 100),
    ("preferred_name", 100),
    ("legal_name", 255),
    ("gender", 50),
    ("date_of_birth", 20),
    ("nationality", 100),
    ("marital_status", 50),
    ("alternate_email", 320),
    ("country_code", 10),
    ("whatsapp_number", 50),
    ("address_line1", 255),
    ("address_line2", 255),
    ("city", 100),
    ("state", 100),
    ("country", 100),
    ("postal_code", 20),
    ("employment_type", 50),
    ("kaggle_url", 500),
    ("leetcode_url", 500),
    ("hackerrank_url", 500),
    ("codechef_url", 500),
    ("geeksforgeeks_url", 500),
    ("stackoverflow_url", 500),
    ("medium_url", 500),
    ("degree", 255),
    ("specialization", 255),
    ("passport_number", 50),
    ("citizenship", 100),
    ("disability_status", 100),
    ("veteran_status", 100),
    ("ethnicity", 100),
    ("time_zone", 100),
]

_FLOAT_COLUMNS = [
    "current_cgpa",
    "percentage",
    "tenth_percentage",
    "twelfth_percentage",
    "relevant_experience_years",
]

_TEXT_COLUMNS = ["academic_achievements", "reason_for_leaving"]

_BOOLEAN_COLUMNS = [
    "is_fresher",
    "work_authorized",
    "requires_visa_sponsorship",
    "immediate_joiner",
]

_JSON_LIST_COLUMNS = ["awards", "publications", "hobbies_interests"]


def upgrade() -> None:
    for name, length in _STRING_COLUMNS:
        op.add_column("profiles", sa.Column(name, sa.String(length), nullable=True))
    for name in _FLOAT_COLUMNS:
        op.add_column("profiles", sa.Column(name, sa.Float(), nullable=True))
    for name in _TEXT_COLUMNS:
        op.add_column("profiles", sa.Column(name, sa.Text(), nullable=True))
    for name in _BOOLEAN_COLUMNS:
        op.add_column("profiles", sa.Column(name, sa.Boolean(), nullable=True))
    for name in _JSON_LIST_COLUMNS:
        op.add_column("profiles", sa.Column(name, sa.JSON(), nullable=False, server_default="[]"))


def downgrade() -> None:
    for name in _JSON_LIST_COLUMNS:
        op.drop_column("profiles", name)
    for name in _BOOLEAN_COLUMNS:
        op.drop_column("profiles", name)
    for name in _TEXT_COLUMNS:
        op.drop_column("profiles", name)
    for name in _FLOAT_COLUMNS:
        op.drop_column("profiles", name)
    for name, _ in _STRING_COLUMNS:
        op.drop_column("profiles", name)
