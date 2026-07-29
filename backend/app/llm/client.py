"""Provider-agnostic LLM wrapper built on LiteLLM.

Defaults to Anthropic (model "claude-sonnet-5"), but supports any
LiteLLM-compatible provider by changing settings.LLM_DEFAULT_MODEL /
LLM_PROVIDER. Embeddings default to OpenAI's text-embedding-3-small.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

import litellm
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger("app.llm")

litellm.drop_params = True  # silently drop params unsupported by a given provider

T = TypeVar("T", bound=BaseModel)

Message = Dict[str, str]


def _resolve_api_key(model: str) -> Optional[str]:
    """Picks the right configured API key from a LiteLLM-style model string's
    provider prefix, so a single LLMClient instance can be pointed at any
    provider (Anthropic, OpenAI, Gemini, OpenRouter) just by changing the
    model string — without silently sending the wrong provider's key.
    """
    if model.startswith("openrouter/"):
        return settings.OPENROUTER_API_KEY or None
    if model.startswith("gemini") or model.startswith("google/"):
        return settings.GEMINI_API_KEY or None
    if model.startswith("gpt-") or model.startswith("openai/") or model.startswith("text-embedding"):
        return settings.OPENAI_API_KEY or None
    if model.startswith("claude") or model.startswith("anthropic/"):
        return settings.ANTHROPIC_API_KEY or None
    return None


class LLMClient:
    """Thin wrapper around litellm.completion / litellm.embedding."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.model = model or settings.LLM_DEFAULT_MODEL
        self._api_key_override = api_key

    def _api_key_for(self, model: str) -> Optional[str]:
        return self._api_key_override or _resolve_api_key(model)

    async def chat(
        self,
        messages: List[Message],
        *,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        **kwargs: Any,
    ) -> str:
        """Plain chat completion, returns text content."""
        effective_model = model or self.model
        response = await litellm.acompletion(
            model=effective_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            api_key=self._api_key_for(effective_model),
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def structured_chat(
        self,
        messages: List[Message],
        output_model: Type[T],
        *,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> T:
        """Chat completion constrained to a Pydantic schema via JSON mode."""
        schema = output_model.model_json_schema()
        system_addendum = (
            "You must respond with ONLY a single valid JSON object matching this "
            f"JSON schema, with no markdown fences or extra commentary:\n{schema}"
        )
        augmented_messages = list(messages) + [{"role": "system", "content": system_addendum}]
        effective_model = model or self.model
        api_key = self._api_key_for(effective_model)
        try:
            response = await litellm.acompletion(
                model=effective_model,
                messages=augmented_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
                api_key=api_key,
                **kwargs,
            )
        except Exception:
            # Some providers/models reject response_format; retry without it.
            response = await litellm.acompletion(
                model=effective_model,
                messages=augmented_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=api_key,
                **kwargs,
            )
        content = response.choices[0].message.content or "{}"
        content = _strip_markdown_fences(content)
        return output_model.model_validate_json(content)

    async def embed(
        self,
        texts: List[str],
        *,
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """Embed a list of texts, returns list of vectors."""
        effective_model = model or settings.EMBEDDING_MODEL
        response = await litellm.aembedding(
            model=effective_model,
            input=texts,
            api_key=self._api_key_for(effective_model),
        )
        return [item["embedding"] for item in response.data]


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def get_llm_client() -> LLMClient:
    return LLMClient()
