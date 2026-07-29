from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exceptions import AuthError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.session import AuthSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, *, email: str, password: str, full_name: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise ConflictError("A user with this email already exists")
        user = await self.user_repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        return user

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        session = AuthSession(
            user_id=user.id,
            refresh_token_hash=_hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.user_repo.db.add(session)
        await self.user_repo.db.flush()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, *, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password")
        if not user.is_active:
            raise AuthError("Account is inactive")
        return await self._issue_tokens(user)

    async def refresh(self, *, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthError("Invalid token type")

        user_id = uuid.UUID(payload["sub"])
        user = await self.user_repo.get(user_id)
        if user is None or not user.is_active:
            raise AuthError("User not found or inactive")

        return await self._issue_tokens(user)
