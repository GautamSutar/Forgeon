"""Regression test for a real production incident: SQLAlchemy's `Enum()`
type binds the Python enum member's *name* (e.g. "SUBMITTED") to the
database by default, not its `.value` ("submitted") — unless
`values_callable` is set. Our Alembic migration created the native Postgres
enum types using the lowercase `.value` strings, so writing an application's
status silently worked for nothing until the exact moment a real approval
flow tried to insert `status="submitted"` and Postgres rejected
`"SUBMITTED"` as not a valid `application_status` label.

This was invisible under the SQLite-backed test suite (SQLite has no native
enum type — it just stores whatever string it's given and reads it back
by the same convention, so round-trips look correct even when the actual
bound value is wrong). This test asserts the DB-bound values directly
against what each column's SQLAlchemy Enum type will actually send,
independent of dialect.
"""
from __future__ import annotations

from app.models.application import Application, ApplicationStatus
from app.models.application_answer import AnswerSource, ApplicationAnswer, QuestionType
from app.models.embedding import Embedding, EmbeddingSourceType


def test_application_status_enum_binds_lowercase_values() -> None:
    assert Application.__table__.c.status.type.enums == [e.value for e in ApplicationStatus]
    # Guards against a Python enum whose member names happen to equal their
    # values (which would mask this bug) — these must differ for the test
    # to actually be exercising the name-vs-value distinction.
    assert any(e.name != e.value for e in ApplicationStatus)


def test_question_type_enum_binds_lowercase_values() -> None:
    assert ApplicationAnswer.__table__.c.question_type.type.enums == [e.value for e in QuestionType]


def test_answer_source_enum_binds_lowercase_values() -> None:
    assert ApplicationAnswer.__table__.c.source.type.enums == [e.value for e in AnswerSource]
    assert any(e.name != e.value for e in AnswerSource)


def test_embedding_source_type_enum_binds_lowercase_values() -> None:
    assert Embedding.__table__.c.source_type.type.enums == [e.value for e in EmbeddingSourceType]
    assert any(e.name != e.value for e in EmbeddingSourceType)
