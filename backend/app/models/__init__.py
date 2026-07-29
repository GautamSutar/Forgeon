"""Import all models so they register on Base.metadata (for Alembic)."""
from app.models.application import Application, ApplicationStatus  # noqa: F401
from app.models.application_answer import (  # noqa: F401
    AnswerSource,
    ApplicationAnswer,
    QuestionType,
)
from app.models.application_log import ApplicationLog  # noqa: F401
from app.models.checkpoint import AgentRun  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.embedding import Embedding, EmbeddingSourceType  # noqa: F401
from app.models.field_alias import FieldAlias  # noqa: F401
from app.models.human_feedback import HumanFeedback  # noqa: F401
from app.models.job_description import JobDescription  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.saved_answer import SavedAnswer  # noqa: F401
from app.models.session import AuthSession  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = [
    "Application",
    "ApplicationStatus",
    "ApplicationAnswer",
    "AnswerSource",
    "QuestionType",
    "ApplicationLog",
    "AgentRun",
    "Company",
    "Embedding",
    "EmbeddingSourceType",
    "FieldAlias",
    "HumanFeedback",
    "JobDescription",
    "Profile",
    "Resume",
    "SavedAnswer",
    "AuthSession",
    "User",
]
