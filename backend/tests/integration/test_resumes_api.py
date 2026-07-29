from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.pdf_helper import build_pdf

pytestmark = pytest.mark.asyncio


RESUME_LINES = [
    "Jane Doe",
    "jane.doe@example.com",
    "Skills",
    "Python, FastAPI, SQL",
    "Experience",
    "Backend Engineer at Acme Corp",
    "- Built payment processing service",
]


async def _register_and_login(client: AsyncClient, email: str = "resume@test.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Resume User"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return login.json()["access_token"]


async def _upload(client: AsyncClient, token: str, set_default: bool = False):
    pdf_bytes = build_pdf(RESUME_LINES)
    return await client.post(
        "/api/v1/resumes/upload",
        headers={"Authorization": f"Bearer {token}"},
        params={"set_default": set_default},
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )


async def test_upload_resume_parses_pdf(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await _upload(client, token, set_default=True)
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "resume.pdf"
    assert body["is_default"] is True
    parsed = body["parsed_data"]
    assert parsed["contact"]["email"] == "jane.doe@example.com"
    assert "Python" in parsed["skills"]


async def test_upload_rejects_non_pdf(client: AsyncClient) -> None:
    token = await _register_and_login(client, "resume2@test.com")
    resp = await client.post(
        "/api/v1/resumes/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )
    assert resp.status_code == 422


async def test_list_get_set_default_and_delete_resume(client: AsyncClient) -> None:
    token = await _register_and_login(client, "resume3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    first = (await _upload(client, token, set_default=True)).json()
    second = (await _upload(client, token, set_default=False)).json()

    listed = await client.get("/api/v1/resumes", headers=headers)
    assert listed.status_code == 200
    assert {r["id"] for r in listed.json()} == {first["id"], second["id"]}

    got = await client.get(f"/api/v1/resumes/{second['id']}", headers=headers)
    assert got.status_code == 200
    assert got.json()["is_default"] is False

    set_default = await client.post(f"/api/v1/resumes/{second['id']}/set-default", headers=headers)
    assert set_default.status_code == 200
    assert set_default.json()["is_default"] is True

    first_after = await client.get(f"/api/v1/resumes/{first['id']}", headers=headers)
    assert first_after.json()["is_default"] is False

    deleted = await client.delete(f"/api/v1/resumes/{first['id']}", headers=headers)
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/resumes/{first['id']}", headers=headers)
    assert missing.status_code == 404


async def test_resumes_require_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/resumes")
    assert resp.status_code in (401, 403)


async def test_upload_succeeds_even_when_embedding_provider_unavailable(client: AsyncClient) -> None:
    """Regression test: a real production incident where OpenRouter (chat
    completions only, no embeddings endpoint) was configured as the LLM
    provider with no separate embeddings key set. `embed()` raised, and
    because resume_service.parse_and_embed() didn't isolate that failure,
    the entire upload crashed with a 500 even though parsing had already
    succeeded. Resume parsing must never fail just because embeddings are
    unavailable — embeddings are a secondary RAG enhancement, not required
    for the upload to be useful.
    """
    from app.llm.client import get_llm_client
    from app.main import app
    from tests.conftest import FakeLLMClient

    class EmbedFailsLLMClient(FakeLLMClient):
        async def embed(self, texts, *, model=None):  # type: ignore[override]
            raise RuntimeError("simulated: embeddings endpoint unavailable on this provider")

    app.dependency_overrides[get_llm_client] = lambda: EmbedFailsLLMClient()
    try:
        token = await _register_and_login(client, "resume-no-embed@test.com")
        resp = await _upload(client, token, set_default=True)
    finally:
        app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient()

    assert resp.status_code == 201
    parsed = resp.json()["parsed_data"]
    assert parsed["contact"]["email"] == "jane.doe@example.com"
    assert "Python" in parsed["skills"]
