"""Shared FastAPI dependencies for building repositories/services per-request."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.llm.client import LLMClient, get_llm_client
from app.repositories.application_repository import ApplicationRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.saved_answer_repository import SavedAnswerRepository
from app.repositories.user_repository import UserRepository
from app.services.answer_generation_service import AnswerGenerationService
from app.services.application_service import ApplicationService
from app.services.auth_service import AuthService
from app.services.embedding_service import EmbeddingService
from app.services.profile_service import ProfileService
from app.services.resume_service import ResumeService
from app.services.retriever_service import RetrieverService
from app.services.storage_service import StorageService, get_storage_service


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_profile_repository(db: AsyncSession = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(db)


def get_resume_repository(db: AsyncSession = Depends(get_db)) -> ResumeRepository:
    return ResumeRepository(db)


def get_application_repository(db: AsyncSession = Depends(get_db)) -> ApplicationRepository:
    return ApplicationRepository(db)


def get_saved_answer_repository(db: AsyncSession = Depends(get_db)) -> SavedAnswerRepository:
    return SavedAnswerRepository(db)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)


def get_profile_service(profile_repo: ProfileRepository = Depends(get_profile_repository)) -> ProfileService:
    return ProfileService(profile_repo)


def get_embedding_service(
    db: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> EmbeddingService:
    return EmbeddingService(db, llm_client)


def get_storage_service_dep() -> StorageService:
    return get_storage_service()


def get_resume_service(
    resume_repo: ResumeRepository = Depends(get_resume_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    storage_service: StorageService = Depends(get_storage_service_dep),
) -> ResumeService:
    return ResumeService(resume_repo, embedding_service, storage_service)


def get_application_service(
    application_repo: ApplicationRepository = Depends(get_application_repository),
    saved_answer_repo: SavedAnswerRepository = Depends(get_saved_answer_repository),
) -> ApplicationService:
    return ApplicationService(application_repo, saved_answer_repo)


def get_retriever_service(
    db: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> RetrieverService:
    return RetrieverService(db, llm_client)


def get_answer_generation_service(llm_client: LLMClient = Depends(get_llm_client)) -> AnswerGenerationService:
    return AnswerGenerationService(llm_client)
