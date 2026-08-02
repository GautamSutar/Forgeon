"""Unit tests for the FLUX.1-dev image generation service.

`AsyncInferenceClient.text_to_image` is monkeypatched rather than hitting
Hugging Face — these test our error translation and persistence logic, not
the provider itself.
"""
from __future__ import annotations

import io
import uuid
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, InferenceTimeoutError
from PIL import Image

from app.core.config import settings
from app.services.image_generation_service import (
    ImageGenerationError,
    ImageGenerationService,
    is_configured,
)

PATCH_TARGET = "huggingface_hub.AsyncInferenceClient.text_to_image"


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


def _http_error(cls, status_code: int, error_text: str) -> HfHubHTTPError:
    """Builds a real huggingface_hub HTTP error with a working
    `.response.status_code` and `.server_message`, matching what the client
    library actually raises."""
    request = httpx.Request("POST", "https://router.huggingface.co/fake")
    response = httpx.Response(status_code, request=request, json={"error": error_text})
    return cls(f"{status_code} error", response=response, server_message=error_text)


@pytest.mark.asyncio
async def test_generate_explains_gated_model() -> None:
    """Regression guard: FLUX.1-dev is gated — this must tell the user to
    accept the license, not just surface a bare HTTP error."""
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    error = _http_error(GatedRepoError, 403, "You don't have access to this gated model")
    service = ImageGenerationService()
    with patch(PATCH_TARGET, new=AsyncMock(side_effect=error)):
        with pytest.raises(ImageGenerationError, match="gated"):
            await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_explains_invalid_api_key_401() -> None:
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    error = _http_error(HfHubHTTPError, 401, "Invalid credentials")
    service = ImageGenerationService()
    with patch(PATCH_TARGET, new=AsyncMock(side_effect=error)):
        with pytest.raises(ImageGenerationError, match="HUGGINGFACE_API_KEY"):
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
    error = _http_error(HfHubHTTPError, 403, error_text)
    service = ImageGenerationService()
    with patch(PATCH_TARGET, new=AsyncMock(side_effect=error)):
        with pytest.raises(ImageGenerationError) as exc_info:
            await service.generate("a cat", user_id=uuid.uuid4())

    message = str(exc_info.value)
    assert "permission" in message.lower()
    assert "settings/tokens" in message
    assert "gated" not in message.lower()
    assert "licence" not in message.lower()


@pytest.mark.asyncio
async def test_generate_explains_model_deprecated_by_provider_410() -> None:
    """Regression guard: hf-inference dropped FLUX.1-dev after this service
    was first wired up (a real HF response: "The requested model is
    deprecated and no longer supported by provider hf-inference"). The
    message must point at checking which providers still serve the model,
    not repeat the gated-model or bad-key guidance."""
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    error = _http_error(
        HfHubHTTPError, 410,
        "The requested model is deprecated and no longer supported by provider hf-inference",
    )
    service = ImageGenerationService()
    with patch(PATCH_TARGET, new=AsyncMock(side_effect=error)):
        with pytest.raises(ImageGenerationError, match="no longer served"):
            await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_explains_timeout() -> None:
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    service = ImageGenerationService()
    with patch(PATCH_TARGET, new=AsyncMock(side_effect=InferenceTimeoutError("timed out"))):
        with pytest.raises(ImageGenerationError, match="didn't respond"):
            await service.generate("a cat", user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_generate_persists_image_bytes_and_returns_a_url(tmp_path) -> None:
    settings.HUGGINGFACE_API_KEY = "hf_fake_token"
    settings.IMAGE_STORAGE_DIR = str(tmp_path)

    fake_image = Image.new("RGB", (8, 8), color=(255, 0, 0))
    user_id = uuid.uuid4()
    service = ImageGenerationService()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=fake_image)):
        image = await service.generate("a minimal coffee logo", user_id=user_id)

    assert image.model == service.model
    assert image.prompt == "a minimal coffee logo"
    assert f"/images/{user_id}/" in image.url
    assert image.url.endswith(".png")

    saved_dir = tmp_path / str(user_id)
    saved_files = list(saved_dir.glob("*.png"))
    assert len(saved_files) == 1
    # Round-trips as a real PNG of the right size, not just non-empty bytes.
    with Image.open(io.BytesIO(saved_files[0].read_bytes())) as saved:
        assert saved.format == "PNG"
        assert saved.size == (8, 8)
