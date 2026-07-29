from __future__ import annotations

import logging
import uuid
from typing import List, Optional

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.embedding import EmbeddingSourceType
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.embedding_service import EmbeddingService
from app.services.resume_parser_service import parse_resume_pdf
from app.services.storage_service import StorageService

logger = logging.getLogger("app.services.resume_service")


class ResumeService:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        embedding_service: EmbeddingService,
        storage_service: StorageService,
    ) -> None:
        self.resume_repo = resume_repo
        self.embedding_service = embedding_service
        self.storage_service = storage_service

    async def upload(
        self,
        *,
        user_id: uuid.UUID,
        filename: str,
        file_bytes: bytes,
        set_default: bool = False,
    ) -> Resume:
        if not filename.lower().endswith(".pdf"):
            raise ValidationAppError("Only PDF resumes are supported in this slice")

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise ValidationAppError(f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB")

        storage_path = await self.storage_service.save(file_bytes, user_id=user_id, filename=filename)

        if set_default:
            await self.resume_repo.clear_default(user_id)

        resume = await self.resume_repo.create(
            user_id=user_id,
            filename=filename,
            storage_path=storage_path,
            is_default=set_default,
        )
        return resume

    async def parse_and_embed(self, resume: Resume) -> Resume:
        file_bytes = await self.storage_service.read(resume.storage_path)

        parsed = parse_resume_pdf(file_bytes)
        raw_text = None
        try:
            from app.services.resume_parser_service import extract_text_from_pdf

            raw_text = extract_text_from_pdf(file_bytes)
        except Exception:
            raw_text = None

        resume = await self.resume_repo.update(
            resume,
            parsed_data=parsed.model_dump(),
            raw_text=raw_text,
        )

        if raw_text:
            # Embedding requires a provider that actually serves an
            # embeddings endpoint (e.g. OpenAI) — a chat-only provider like
            # OpenRouter, or no key at all, must not fail the whole upload.
            # Parsing (skills/experience/education/etc.) already succeeded
            # and is the primary value of this endpoint; embeddings are a
            # secondary enhancement for RAG retrieval.
            try:
                chunks = self.embedding_service.chunk_text(raw_text)
                await self.embedding_service.embed_and_store(
                    user_id=resume.user_id,
                    source_type=EmbeddingSourceType.RESUME_CHUNK,
                    content_chunks=chunks,
                    source_id=resume.id,
                )
            except Exception as exc:
                logger.warning(
                    "Resume embedding failed for resume %s (upload/parse still succeeded): %s",
                    resume.id,
                    exc,
                )
        return resume

    async def list_for_user(self, user_id: uuid.UUID) -> List[Resume]:
        return await self.resume_repo.list_by_user(user_id)

    async def get_owned(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        resume = await self.resume_repo.get(resume_id)
        if resume is None or resume.user_id != user_id:
            raise NotFoundError("Resume not found")
        return resume

    async def set_default(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        resume = await self.get_owned(user_id, resume_id)
        await self.resume_repo.clear_default(user_id)
        return await self.resume_repo.update(resume, is_default=True)

    async def delete(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> None:
        resume = await self.get_owned(user_id, resume_id)
        await self.storage_service.delete(resume.storage_path)
        await self.resume_repo.delete(resume)
