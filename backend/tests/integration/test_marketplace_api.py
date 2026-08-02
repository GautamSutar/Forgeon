"""Marketplace catalog + agent chat: browsing, conversation persistence, and
the ownership boundary between users."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

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
    up front rather than appearing usable and failing at call time."""
    resp = await client.get("/api/v1/marketplace/agents")
    by_slug = {a["slug"]: a for a in resp.json()}

    for slug in ("image", "video", "mobile"):
        assert by_slug[slug]["status"] == "requires_setup"
        assert by_slug[slug]["setup_hint"]

    assert by_slug["job"]["status"] == "live"


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
