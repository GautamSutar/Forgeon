"""Unit tests for the FLUX.1-dev image generation service. httpx is
monkeypatched rather than hitting Hugging Face — these test our error
translation and persistence logic, not the provider itself."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import settings
from app.services.image_generation_service import (
    ImageGenerationError,
    ImageGenerationService,
    is_configured,
)


@pytest.fixture(autouse=True)
def _reset_hf_key():
    original = settings.HUGGINGFACE_API_KEY
    yield
    settings.HUGGINGFACE_API_KEY = original


def test_is_configured_reflects_the_api_key_setting() -> None:
    settings.HUGGINGFACE_API_KEY = ""
    assert is_configured() is False
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    assert is_configured() is True


@pytest.mark.asyncio
async def test_generate_refuses_when_not_configured() -> None:
    settings.HUGGINGFACE_API_KEY = ""
    service = ImageGenerationService()
    with pytest.raises(ImageGenerationError, match="HUGGINGFACE_API_KEY"):
        await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_refuses_an_empty_prompt() -> None:
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    service = ImageGenerationService()
    with pytest.raises(ImageGenerationError, match="Describe the image"):
        await service.generate("   ", user_id=uuid.uuid4())


def _mock_client(response: SimpleNamespace):
    """Builds an `httpx.AsyncClient()` async-context-manager mock whose
    `.post()` resolves to the given fake response."""
    client = AsyncMock()
    client.post = AsyncMock(return_value=response)
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


@pytest.mark.asyncio
async def test_generate_explains_gated_model_403() -> None:
    """Regression guard: FLUX.1-dev is gated — a 403 must tell the user to
    accept the license, not just surface a bare HTTP error."""
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    response = SimpleNamespace(
        status_code=403,
        headers={"content-type": "application/json"},
        json=lambda: {"error": "forbidden"},
        text="forbidden",
        content=b"",
    )
    service = ImageGenerationService()
    with patch("httpx.AsyncClient", return_value=_mock_client(response)):
        with pytest.raises(ImageGenerationError, match="gated"):
            await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_distinguishes_missing_token_permission_from_gating() -> None:
    """Regression guard: a real HF response observed in production —
    '...does not have sufficient permissions to call Inference Providers...'
    — also arrives as a 403, but the fix is enabling a token permission, not
    accepting a model license. Telling the user to do the wrong one wastes a
    round trip, so the two must not share a message."""
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    error_text = (
        "This authentication method does not have sufficient permissions to "
        "call Inference Providers on behalf of user someuser"
    )
    response = SimpleNamespace(
        status_code=403,
        headers={"content-type": "application/json"},
        json=lambda: {"error": error_text},
        text=error_text,
        content=b"",
    )
    service = ImageGenerationService()
    with patch("httpx.AsyncClient", return_value=_mock_client(response)):
        with pytest.raises(ImageGenerationError) as exc_info:
            await service.generate("a cat", user_id=uuid.uuid4())

    message = str(exc_info.value)
    assert "permission" in message.lower()
    assert "settings/tokens" in message
    assert "gated" not in message.lower()
    assert "licence" not in message.lower()


@pytest.mark.asyncio
async def test_generate_explains_invalid_api_key_401() -> None:
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    response = SimpleNamespace(
        status_code=401,
        headers={"content-type": "application/json"},
        json=lambda: {"error": "invalid token"},
        text="invalid token",
        content=b"",
    )
    service = ImageGenerationService()
    with patch("httpx.AsyncClient", return_value=_mock_client(response)):
        with pytest.raises(ImageGenerationError, match="HUGGINGFACE_API_KEY"):
            await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_treats_a_json_body_on_200_as_an_error() -> None:
    """HF sometimes returns 200 with a JSON error payload instead of image
    bytes (e.g. still loading) — this must not be persisted as an image."""
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    response = SimpleNamespace(
        status_code=200,
        headers={"content-type": "application/json"},
        json=lambda: {"error": "Model is currently loading"},
        text="",
        content=b"",
    )
    service = ImageGenerationService()
    with patch("httpx.AsyncClient", return_value=_mock_client(response)):
        with pytest.raises(ImageGenerationError, match="loading"):
            await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_persists_image_bytes_and_returns_a_url(tmp_path) -> None:
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    settings.IMAGE_STORAGE_DIR = str(tmp_path)
    response = SimpleNamespace(
        status_code=200,
        headers={"content-type": "image/png"},
        json=lambda: {},
        text="",
        content=b"\x89PNG\r\n\x1a\nfake-png-bytes",
    )
    user_id = uuid.uuid4()
    service = ImageGenerationService()
    with patch("httpx.AsyncClient", return_value=_mock_client(response)):
        image = await service.generate("a minimal coffee logo", user_id=user_id)

    assert image.model == service.model
    assert image.prompt == "a minimal coffee logo"
    assert f"/images/{user_id}/" in image.url
    assert image.url.endswith(".png")

    saved_dir = tmp_path / str(user_id)
    saved_files = list(saved_dir.glob("*.png"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == response.content
