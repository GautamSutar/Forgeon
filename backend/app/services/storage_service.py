"""Pluggable file storage: local disk by default, Cloudinary when
CLOUDINARY_URL is configured. Resume PDFs contain PII (name, phone, email,
address), so the Cloudinary backend uploads as a private "authenticated"
asset rather than Cloudinary's default public delivery, and generates a
short-lived signed URL on demand for reads instead of persisting one.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from typing import Protocol

import httpx

from app.core.config import settings

CLOUDINARY_PREFIX = "cloudinary://"


class StorageService(Protocol):
    async def save(self, file_bytes: bytes, *, user_id: uuid.UUID, filename: str) -> str: ...

    async def read(self, storage_path: str) -> bytes: ...

    async def delete(self, storage_path: str) -> None: ...


class LocalStorageService:
    """Writes to local disk under settings.RESUME_STORAGE_DIR. Used when
    Cloudinary isn't configured, so the app stays fully functional without
    any cloud storage credentials.
    """

    async def save(self, file_bytes: bytes, *, user_id: uuid.UUID, filename: str) -> str:
        storage_dir = os.path.join(settings.RESUME_STORAGE_DIR, str(user_id))
        os.makedirs(storage_dir, exist_ok=True)
        unique_name = f"{uuid.uuid4()}_{filename}"
        storage_path = os.path.join(storage_dir, unique_name)
        with open(storage_path, "wb") as f:
            f.write(file_bytes)
        return storage_path

    async def read(self, storage_path: str) -> bytes:
        with open(storage_path, "rb") as f:
            return f.read()

    async def delete(self, storage_path: str) -> None:
        if os.path.exists(storage_path):
            try:
                os.remove(storage_path)
            except OSError:
                pass


class CloudinaryStorageService:
    """Stores resumes in Cloudinary as private "raw" assets.

    `storage_path` values from this backend are `cloudinary://<public_id>`
    identifiers, not fetchable URLs — a persisted signed URL would eventually
    expire, so the signature is generated fresh on every read instead.
    """

    def __init__(self) -> None:
        import cloudinary

        cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)

    async def save(self, file_bytes: bytes, *, user_id: uuid.UUID, filename: str) -> str:
        import cloudinary.uploader

        public_id = f"resumes/{user_id}/{uuid.uuid4()}"

        def _upload() -> dict:
            return cloudinary.uploader.upload(
                file_bytes,
                public_id=public_id,
                resource_type="raw",
                type="authenticated",
                overwrite=False,
            )

        result = await asyncio.to_thread(_upload)
        return f"{CLOUDINARY_PREFIX}{result['public_id']}"

    async def read(self, storage_path: str) -> bytes:
        url = self._signed_url(storage_path)
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def delete(self, storage_path: str) -> None:
        import cloudinary.uploader

        public_id = storage_path.removeprefix(CLOUDINARY_PREFIX)

        def _destroy() -> None:
            cloudinary.uploader.destroy(public_id, resource_type="raw", type="authenticated")

        await asyncio.to_thread(_destroy)

    def _signed_url(self, storage_path: str) -> str:
        import cloudinary.utils

        public_id = storage_path.removeprefix(CLOUDINARY_PREFIX)
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            resource_type="raw",
            type="authenticated",
            sign_url=True,
        )
        return url


def get_storage_service() -> StorageService:
    if settings.CLOUDINARY_URL:
        return CloudinaryStorageService()
    return LocalStorageService()
