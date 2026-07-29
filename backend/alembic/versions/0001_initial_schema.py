"""Initial schema: users, profiles, resumes, companies, job_descriptions,
applications, application_answers, saved_answers, field_aliases, embeddings,
application_logs, sessions, human_feedback, checkpoints (run metadata).

Revision ID: 0001
Revises:
Create Date: 2026-07-28
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # create_type=False on every enum used below: they're explicitly created
    # once via .create(checkfirst=True) here, so the column type objects
    # must not *also* try to create them during CREATE TABLE — otherwise
    # SQLAlchemy emits a second CREATE TYPE and Postgres raises
    # DuplicateObjectError.
    application_status_enum = postgresql.ENUM(
        "draft", "pending_approval", "approved", "rejected", "submitted", "failed",
        name="application_status",
        create_type=False,
    )
    question_type_enum = postgresql.ENUM("static", "dynamic", name="question_type", create_type=False)
    answer_source_enum = postgresql.ENUM(
        "profile", "generated", "saved_answer", name="answer_source", create_type=False
    )
    embedding_source_type_enum = postgresql.ENUM(
        "resume_chunk", "project", "skill", "saved_answer", "interview_answer", "company_note",
        name="embedding_source_type",
        create_type=False,
    )

    bind = op.get_bind()
    application_status_enum.create(bind, checkfirst=True)
    question_type_enum.create(bind, checkfirst=True)
    answer_source_enum.create(bind, checkfirst=True)
    embedding_source_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_companies_name", "companies", ["name"])

    op.create_table(
        "job_descriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "company_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="SET NULL", name="fk_job_descriptions_company_id_companies"),
            nullable=True,
        ),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("role_title", sa.String(255), nullable=True),
        sa.Column("skills", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("responsibilities", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("requirements", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("nice_to_have", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("experience_required", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_job_descriptions_company_id", "job_descriptions", ["company_id"])

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_profiles_user_id_users"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("portfolio_url", sa.String(500), nullable=True),
        sa.Column("current_salary", sa.Float(), nullable=True),
        sa.Column("expected_salary", sa.Float(), nullable=True),
        sa.Column("notice_period_days", sa.Integer(), nullable=True),
        sa.Column("years_experience", sa.Float(), nullable=True),
        sa.Column("visa_status", sa.String(100), nullable=True),
        sa.Column("preferred_locations", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("preferred_roles", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_profiles_user_id", "profiles", ["user_id"])
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"])

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_resumes_user_id_users"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("parsed_data", postgresql.JSONB(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_applications_user_id_users"),
            nullable=False,
        ),
        sa.Column(
            "company_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="SET NULL", name="fk_applications_company_id_companies"),
            nullable=True,
        ),
        sa.Column(
            "job_description_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "job_descriptions.id", ondelete="SET NULL",
                name="fk_applications_job_description_id_job_descriptions",
            ),
            nullable=True,
        ),
        sa.Column(
            "resume_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resumes.id", ondelete="RESTRICT", name="fk_applications_resume_id_resumes"),
            nullable=False,
        ),
        sa.Column("role_title", sa.String(255), nullable=True),
        sa.Column("status", application_status_enum, nullable=False, server_default="draft"),
        sa.Column("ats_platform", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("screenshot_path", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_company_id", "applications", ["company_id"])
    op.create_index("ix_applications_job_description_id", "applications", ["job_description_id"])
    op.create_index("ix_applications_status", "applications", ["status"])

    op.create_table(
        "application_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "application_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "applications.id", ondelete="CASCADE", name="fk_application_answers_application_id_applications"
            ),
            nullable=False,
        ),
        sa.Column("field_label", sa.String(500), nullable=False),
        sa.Column("field_name", sa.String(255), nullable=False),
        sa.Column("canonical_key", sa.String(100), nullable=True),
        sa.Column("question_type", question_type_enum, nullable=False),
        sa.Column("generated_answer", sa.Text(), nullable=True),
        sa.Column("final_answer", sa.Text(), nullable=True),
        sa.Column("was_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source", answer_source_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_application_answers_application_id", "application_answers", ["application_id"])

    op.create_table(
        "saved_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_saved_answers_user_id_users"),
            nullable=False,
        ),
        sa.Column("canonical_key", sa.String(100), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_saved_answers_user_id", "saved_answers", ["user_id"])
    op.create_index("ix_saved_answers_canonical_key", "saved_answers", ["canonical_key"])

    op.create_table(
        "field_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("canonical_key", sa.String(100), nullable=False),
        sa.Column("alias_label", sa.String(500), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_field_aliases_canonical_key", "field_aliases", ["canonical_key"])

    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_embeddings_user_id_users"),
            nullable=False,
        ),
        sa.Column("source_type", embedding_source_type_enum, nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_embeddings_user_id", "embeddings", ["user_id"])
    op.create_index("ix_embeddings_source_type", "embeddings", ["source_type"])
    op.execute(
        "CREATE INDEX ix_embeddings_embedding_hnsw ON embeddings "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "application_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "application_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "applications.id", ondelete="CASCADE", name="fk_application_logs_application_id_applications"
            ),
            nullable=True,
        ),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_application_logs_application_id", "application_logs", ["application_id"])

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_sessions_user_id_users"),
            nullable=False,
        ),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_refresh_token_hash", "sessions", ["refresh_token_hash"])

    op.create_table(
        "human_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "application_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "applications.id", ondelete="CASCADE", name="fk_human_feedback_application_id_applications"
            ),
            nullable=False,
        ),
        sa.Column("field_name", sa.String(255), nullable=False),
        sa.Column("original_value", sa.Text(), nullable=True),
        sa.Column("edited_value", sa.Text(), nullable=True),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_human_feedback_application_id", "human_feedback", ["application_id"])

    op.create_table(
        "checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("run_id", sa.String(255), nullable=False),
        sa.Column("thread_id", sa.String(255), nullable=False),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_checkpoints_user_id_users"),
            nullable=False,
        ),
        sa.Column(
            "application_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "applications.id", ondelete="SET NULL", name="fk_checkpoints_application_id_applications"
            ),
            nullable=True,
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="running"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_checkpoints_run_id", "checkpoints", ["run_id"])
    op.create_index("ix_checkpoints_run_id", "checkpoints", ["run_id"])
    op.create_index("ix_checkpoints_thread_id", "checkpoints", ["thread_id"])
    op.create_index("ix_checkpoints_user_id", "checkpoints", ["user_id"])
    op.create_index("ix_checkpoints_application_id", "checkpoints", ["application_id"])


def downgrade() -> None:
    op.drop_table("checkpoints")
    op.drop_table("human_feedback")
    op.drop_table("sessions")
    op.drop_table("application_logs")
    op.drop_table("embeddings")
    op.drop_table("field_aliases")
    op.drop_table("saved_answers")
    op.drop_table("application_answers")
    op.drop_table("applications")
    op.drop_table("resumes")
    op.drop_table("profiles")
    op.drop_table("job_descriptions")
    op.drop_table("companies")
    op.drop_table("users")

    bind = op.get_bind()
    postgresql.ENUM(name="embedding_source_type").drop(bind, checkfirst=True)
    postgresql.ENUM(name="answer_source").drop(bind, checkfirst=True)
    postgresql.ENUM(name="question_type").drop(bind, checkfirst=True)
    postgresql.ENUM(name="application_status").drop(bind, checkfirst=True)
