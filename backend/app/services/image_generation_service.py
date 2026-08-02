"""Text-to-image generation via the Hugging Face Inference API.

Defaults to `black-forest-labs/FLUX.1-dev`. Two things about that model are
worth knowing before wiring it into anything user-facing:

- **It is gated.** The account behind ``HUGGINGFACE_API_KEY`` must accept the
  licence at huggingface.co/black-forest-labs/FLUX.1-dev first, or every
  request returns 403.
- **Its licence is non-commercial.** Use `black-forest-labs/FLUX.1-schnell`
  (Apache-2.0) for commercial work — set ``IMAGE_MODEL`` to switch.

Generated images are written through the existing storage layer, so they
land on local disk or in Cloudinary with the same code path as resumes.
"""
from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass

import httpx

from app.core.config import settings

logger = logging.getLogger("app.services.image_generation")

# Hugging Face retired the legacy api-inference.huggingface.co host in favor
# of the Inference Providers router. The `hf-inference` provider segment
# routes to HF's own first-party inference backend — the direct successor to
# the old serverless Inference API — and keeps the same request/response
# shape this service already relies on.
HF_INFERENCE_BASE = "https://router.huggingface.co/hf-inference/models"


class ImageGenerationError(Exception):
    """Raised with a message intended to be shown to the user verbatim."""


@dataclass
class GeneratedImage:
    url: str
    prompt: str
    model: str


def is_configured() -> bool:
    return bool(settings.HUGGINGFACE_API_KEY)


class ImageGenerationService:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.IMAGE_MODEL

    async def generate(self, prompt: str, *, user_id: uuid.UUID) -> GeneratedImage:
        if not is_configured():
            raise ImageGenerationError(
                "Image generation isn't configured. Add HUGGINGFACE_API_KEY to "
                "backend/.env, and make sure that account has accepted the "
                "licence at huggingface.co/black-forest-labs/FLUX.1-dev."
            )

        cleaned = prompt.strip()
        if not cleaned:
            raise ImageGenerationError("Describe the image you want generated.")

        payload = {
            "inputs": cleaned,
            # `wait_for_model` makes HF hold the request open through a cold
            # start instead of returning 503 and forcing the caller to poll.
            "options": {"wait_for_model": True},
        }

        try:
            async with httpx.AsyncClient(timeout=settings.IMAGE_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{HF_INFERENCE_BASE}/{self.model}",
                    headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise ImageGenerationError(
                f"The model didn't respond within {settings.IMAGE_TIMEOUT_SECONDS}s. "
                "Large diffusion models can be slow to cold-start — try again in a minute."
            ) from exc
        except httpx.HTTPError as exc:
            raise ImageGenerationError(f"Couldn't reach the image provider: {exc}") from exc

        if response.status_code != 200:
            raise ImageGenerationError(self._explain_failure(response))

        # A 200 carrying JSON rather than image bytes is still an error
        # payload (HF returns {"error": ...} with 200 in some states).
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            detail = response.json()
            raise ImageGenerationError(
                str(detail.get("error") or detail) if isinstance(detail, dict) else str(detail)
            )

        url = await self._persist(response.content, user_id=user_id)
        return GeneratedImage(url=url, prompt=cleaned, model=self.model)

    def _explain_failure(self, response: httpx.Response) -> str:
        """Turns provider status codes into something the user can act on."""
        body = ""
        try:
            data = response.json()
            body = str(data.get("error", "")) if isinstance(data, dict) else str(data)
        except Exception:
            body = response.text[:200]

        if response.status_code == 401:
            return "Hugging Face rejected the API key. Check HUGGINGFACE_API_KEY in backend/.env."
        if response.status_code == 403:
            # A 403 here has two unrelated causes with near-identical HTTP
            # shape, so branch on HF's actual error text rather than
            # guessing — telling a user to accept a license they've already
            # accepted (or vice versa) just burns another round trip.
            if "permission" in body.lower() or "inference providers" in body.lower():
                return (
                    "Hugging Face rejected this token for Inference Providers: "
                    f'"{body}". Fine-grained tokens need the "Make calls to '
                    "Inference Providers\" permission enabled — edit the token at "
                    "huggingface.co/settings/tokens (or create a new one with that "
                    "permission checked) and update HUGGINGFACE_API_KEY."
                )
            return (
                f"Access to {self.model} is gated. Open "
                f"huggingface.co/{self.model} while signed in as the token's "
                f'account and accept the licence, then try again. ({body})'
            )
        if response.status_code == 404:
            return f"Model {self.model} was not found on Hugging Face. Check IMAGE_MODEL."
        if response.status_code == 429:
            return "Rate limited by Hugging Face. Wait a moment and try again."
        if response.status_code == 503:
            return "The model is still loading on Hugging Face. Try again shortly."
        return f"Image generation failed ({response.status_code}). {body}".strip()

    async def _persist(self, image_bytes: bytes, *, user_id: uuid.UUID) -> str:
        """Writes the PNG to disk and returns the URL the API serves it from.

        Stored per-user so the read endpoint can enforce ownership from the
        path alone.
        """
        directory = os.path.join(settings.IMAGE_STORAGE_DIR, str(user_id))
        os.makedirs(directory, exist_ok=True)
        name = f"{uuid.uuid4()}.png"
        with open(os.path.join(directory, name), "wb") as f:
            f.write(image_bytes)
        return f"{settings.API_V1_PREFIX}/images/{user_id}/{name}"
