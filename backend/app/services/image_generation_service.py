"""Text-to-image generation via the Hugging Face Inference Providers.

Defaults to `black-forest-labs/FLUX.1-dev`. Uses `huggingface_hub`'s
`AsyncInferenceClient` rather than hand-rolled HTTP calls against a router
URL — Hugging Face has changed the serving details under this model twice in
one day during development: the legacy `api-inference.huggingface.co` host
was decommissioned in favor of `router.huggingface.co`, and then `hf-inference`
(HF's own first-party backend) stopped serving this model in favor of
third-party providers (fal, Replicate, WaveSpeed). `provider="auto"` asks HF
to pick whichever backend currently serves the model, so this stops being our
problem to track — it's the official client library's job to stay current
with HF's own routing changes, not ours.

Three things about this model are worth knowing before wiring it into
anything user-facing:

- **It is gated.** The account behind ``HUGGINGFACE_API_KEY`` must accept the
  licence at huggingface.co/black-forest-labs/FLUX.1-dev first.
- **The token needs an explicit permission.** Fine-grained tokens must have
  "Make calls to Inference Providers" checked, separately from model access —
  a token can have accepted the license and still be rejected for this.
- **Its licence is non-commercial.** Use `black-forest-labs/FLUX.1-schnell`
  (Apache-2.0) for commercial work — set ``IMAGE_MODEL`` to switch.

Generated images are written through the existing storage layer, so they
land on local disk with the same code path as resumes.
"""
from __future__ import annotations

import io
import logging
import os
import uuid
from dataclasses import dataclass

from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, InferenceTimeoutError

from app.core.config import settings

logger = logging.getLogger("app.services.image_generation")


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

        client = AsyncInferenceClient(
            provider=settings.IMAGE_PROVIDER,
            token=settings.HUGGINGFACE_API_KEY,
            timeout=settings.IMAGE_TIMEOUT_SECONDS,
        )

        try:
            image = await client.text_to_image(cleaned, model=self.model)
        except GatedRepoError as exc:
            raise ImageGenerationError(
                f"Access to {self.model} is gated. Open "
                f"huggingface.co/{self.model} while signed in as the token's "
                "account and accept the licence, then try again."
            ) from exc
        except InferenceTimeoutError as exc:
            raise ImageGenerationError(
                f"The model didn't respond within {settings.IMAGE_TIMEOUT_SECONDS}s. "
                "Large diffusion models can be slow to cold-start — try again in a minute."
            ) from exc
        except HfHubHTTPError as exc:
            raise ImageGenerationError(self._explain_failure(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise ImageGenerationError(f"Couldn't reach the image provider: {exc}") from exc

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        url = await self._persist(buffer.getvalue(), user_id=user_id)
        return GeneratedImage(url=url, prompt=cleaned, model=self.model)

    def _explain_failure(self, exc: HfHubHTTPError) -> str:
        """Turns a raw huggingface_hub HTTP error into something the user can
        act on. `exc.server_message` is HF's parsed error text, when present."""
        status = exc.response.status_code
        body = exc.server_message or str(exc)

        if status == 401:
            return "Hugging Face rejected the API key. Check HUGGINGFACE_API_KEY in backend/.env."
        if status == 403:
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
        if status == 404:
            return f"Model {self.model} was not found on Hugging Face. Check IMAGE_MODEL."
        if status == 410:
            return (
                f"{self.model} is no longer served by its current provider. "
                "This can happen even with provider=\"auto\" if every provider "
                "listed on the model's page has dropped it — check "
                f"huggingface.co/{self.model} for which providers still serve it, "
                "or switch IMAGE_MODEL to a different model."
            )
        if status == 429:
            return "Rate limited by Hugging Face. Wait a moment and try again."
        if status == 503:
            return "The model is still loading on Hugging Face. Try again shortly."
        return f"Image generation failed ({status}). {body}".strip()

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
