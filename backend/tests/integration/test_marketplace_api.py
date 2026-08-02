"""Marketplace catalog + agent chat: browsing, conversation persistence, and
the ownership boundary between users."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.services.image_generation_service import GeneratedImage

pytestmark = pytest.mark.asyncio


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Market User"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return login.json()["access_token"]


async def test_browse_agents_returns_full_catalog(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/marketplace/agents")
    assert resp.status_code == 200
    agents = resp.json()

    assert len(agents) == 10
    slugs = {a["slug"] for a in agents}
    assert slugs == {
        "job", "resume", "email", "research", "coding",
        "travel", "finance", "image", "video", "mobile",
    }


async def test_agents_requiring_setup_declare_it_with_a_hint(client: AsyncClient) -> None:
    """Agents whose core capability needs an unconfigured provider must say so
    up front rather than appearing usable and failing at call time.

    Forces HUGGINGFACE_API_KEY off for the duration: the image agent's
    status is computed from that setting (see test_marketplace endpoint),
    so this must not depend on whatever happens to be in the developer's
    real backend/.env — a locally-configured key would otherwise flip
    "image" to live and silently break this assertion."""
    original = settings.HUGGINGFACE_API_KEY
    settings.HUGGINGFACE_API_KEY = ""
    try:
        resp = await client.get("/api/v1/marketplace/agents")
        by_slug = {a["slug"]: a for a in resp.json()}

        for slug in ("image", "video", "mobile"):
            assert by_slug[slug]["status"] == "requires_setup"
            assert by_slug[slug]["setup_hint"]
    finally:
        settings.HUGGINGFACE_API_KEY = original

    assert by_slug["job"]["status"] == "live"


async def test_image_agent_reports_live_once_configured(client: AsyncClient) -> None:
    """The catalog's `status` for the image agent isn't a static flag — it
    tracks whether HUGGINGFACE_API_KEY is actually set, so the marketplace
    can't lie about an agent being usable."""
    original = settings.HUGGINGFACE_API_KEY
    settings.HUGGINGFACE_API_KEY = "hf_fake_token_for_test"
    try:
        resp = await client.get("/api/v1/marketplace/agents/image")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "live"
        assert body["setup_hint"] is None
    finally:
        settings.HUGGINGFACE_API_KEY = original


async def test_image_agent_chat_generates_instead_of_conversing(client: AsyncClient) -> None:
    """A message to the image agent is a generation prompt, not a question —
    it must route to ImageGenerationService, never to the chat LLM."""
    token = await _register_and_login(client, "image-agent@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    fake_image = GeneratedImage(
        url="/api/v1/images/fake-user/fake-file.png",
        prompt="a minimal coffee logo",
        model="black-forest-labs/FLUX.1-dev",
    )
    with patch(
        "app.services.agent_chat_service.ImageGenerationService.generate",
        new=AsyncMock(return_value=fake_image),
    ):
        resp = await client.post(
            "/api/v1/marketplace/agents/image/chat",
            headers=headers,
            json={"message": "a minimal coffee logo"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["message"]["role"] == "assistant"
    assert "fake-file.png" in body["message"]["content"]
    assert "black-forest-labs/FLUX.1-dev" in body["message"]["content"]

    detail = await client.get(
        f"/api/v1/marketplace/conversations/{body['conversation_id']}", headers=headers
    )
    messages = detail.json()["messages"]
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "a minimal coffee logo"


async def test_image_agent_chat_surfaces_generation_failure_in_transcript(client: AsyncClient) -> None:
    """When HUGGINGFACE_API_KEY isn't configured, the failure must show up as
    an assistant reply the user can read — not a 500, and not a silently
    empty response.

    Forced off explicitly rather than relying on it being unset by default:
    a real key in the developer's backend/.env would otherwise make this
    test attempt a genuine network call to Hugging Face."""
    original = settings.HUGGINGFACE_API_KEY
    settings.HUGGINGFACE_API_KEY = ""
    try:
        token = await _register_and_login(client, "image-agent-fail@test.com")
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            "/api/v1/marketplace/agents/image/chat",
            headers=headers,
            json={"message": "a minimal coffee logo"},
        )
        assert resp.status_code == 200
        assert "HUGGINGFACE_API_KEY" in resp.json()["message"]["content"]
    finally:
        settings.HUGGINGFACE_API_KEY = original


async def test_unknown_agent_slug_404s(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/marketplace/agents/does-not-exist")
    assert resp.status_code == 404


async def test_chat_creates_conversation_and_persists_both_turns(client: AsyncClient) -> None:
    token = await _register_and_login(client, "chat@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/marketplace/agents/email/chat",
        headers=headers,
        json={"message": "Draft a follow-up email after an interview."},
    )
    assert resp.status_code == 200
    body = resp.json()
    conversation_id = body["conversation_id"]
    assert body["message"]["role"] == "assistant"

    detail = await client.get(f"/api/v1/marketplace/conversations/{conversation_id}", headers=headers)
    messages = detail.json()["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert messages[0]["content"] == "Draft a follow-up email after an interview."
    # First exchange names the thread instead of leaving it "New chat".
    assert detail.json()["title"] != "New chat"


async def test_chat_continues_an_existing_conversation(client: AsyncClient) -> None:
    token = await _register_and_login(client, "chat2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        "/api/v1/marketplace/agents/coding/chat",
        headers=headers,
        json={"message": "Explain this function."},
    )
    conversation_id = first.json()["conversation_id"]

    await client.post(
        "/api/v1/marketplace/agents/coding/chat",
        headers=headers,
        json={"message": "Now write a test for it.", "conversation_id": conversation_id},
    )

    detail = await client.get(f"/api/v1/marketplace/conversations/{conversation_id}", headers=headers)
    assert len(detail.json()["messages"]) == 4  # two full exchanges, one thread

    listing = await client.get("/api/v1/marketplace/agents/coding/conversations", headers=headers)
    assert len(listing.json()) == 1


async def test_conversations_are_scoped_to_their_owner(client: AsyncClient) -> None:
    """A conversation belonging to another user must 404 — not 403, which
    would confirm the ID exists to someone probing for it."""
    owner_token = await _register_and_login(client, "owner@test.com")
    other_token = await _register_and_login(client, "other@test.com")

    created = await client.post(
        "/api/v1/marketplace/agents/research/chat",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"message": "Summarize these notes."},
    )
    conversation_id = created.json()["conversation_id"]

    resp = await client.get(
        f"/api/v1/marketplace/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 404

    resp = await client.delete(
        f"/api/v1/marketplace/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 404


async def test_chat_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/marketplace/agents/email/chat", json={"message": "hello"}
    )
    assert resp.status_code in (401, 403)
