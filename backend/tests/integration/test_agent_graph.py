"""End-to-end test of the LangGraph human-in-the-loop flow through the
/agent REST endpoints: run -> interrupted at human_approval -> approve ->
submitted -> saved to history. Also covers the reject path, and asserts the
never-auto-submit guarantee holds when a run is rejected.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.pdf_helper import build_pdf

pytestmark = pytest.mark.asyncio

FORM_HTML = """
<form>
  <label for="fname">Full Name</label>
  <input type="text" id="fname" name="full_name" required />

  <label for="email">Email Address</label>
  <input type="email" id="email" name="email" required />

  <textarea name="cover_letter" placeholder="Why do you want this role?"></textarea>

  <button type="submit">Submit</button>
</form>
"""

JOB_DESCRIPTION = (
    "We are hiring a Backend Engineer at Acme Corp. Required skills: Python, "
    "FastAPI, PostgreSQL. 3+ years of experience required."
)


async def _register_and_login(client: AsyncClient, email: str = "agent@test.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Agent User"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return login.json()["access_token"]


async def _upload_default_resume(client: AsyncClient, token: str) -> str:
    resp = await client.post(
        "/api/v1/resumes/upload",
        headers={"Authorization": f"Bearer {token}"},
        params={"set_default": True},
        files={
            "file": (
                "resume.pdf",
                build_pdf(["Jane Doe", "jane.doe@example.com", "Skills", "Python, FastAPI"]),
                "application/pdf",
            )
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_agent_run_pauses_for_human_approval(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    await _upload_default_resume(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/agent/run",
        headers=headers,
        json={"html": FORM_HTML, "job_description": JOB_DESCRIPTION},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["status"] == "interrupted"
    assert body["run_id"]
    assert body["preview"] is not None
    assert "fields" in body["preview"]
    assert body["application_status"] is None


async def test_agent_approve_resumes_and_submits(client: AsyncClient) -> None:
    token = await _register_and_login(client, "agent2@test.com")
    await _upload_default_resume(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    run_resp = await client.post(
        "/api/v1/agent/run",
        headers=headers,
        json={"html": FORM_HTML, "job_description": JOB_DESCRIPTION},
    )
    run_id = run_resp.json()["run_id"]
    assert run_resp.json()["status"] == "interrupted"

    approve_resp = await client.post(
        f"/api/v1/agent/{run_id}/approve",
        headers=headers,
        json={"edited_answers": {}},
    )
    assert approve_resp.status_code == 200
    body = approve_resp.json()

    assert body["status"] == "completed"
    assert body["application_status"] == "submitted"
    assert body["application_id"] is not None

    application = await client.get(f"/api/v1/applications/{body['application_id']}", headers=headers)
    assert application.status_code == 200
    assert application.json()["status"] == "submitted"


async def test_agent_run_persists_ats_platform_and_source_url(client: AsyncClient) -> None:
    """Regression test: the browser extension detects the ATS platform and
    page URL client-side, but the backend previously had no field to accept
    them, so every saved Application showed "unknown platform" regardless of
    what was actually detected."""
    token = await _register_and_login(client, "agent-platform@test.com")
    await _upload_default_resume(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    run_resp = await client.post(
        "/api/v1/agent/run",
        headers=headers,
        json={
            "html": FORM_HTML,
            "job_description": JOB_DESCRIPTION,
            "ats_platform": "greenhouse",
            "source_url": "https://boards.greenhouse.io/acme/jobs/123",
        },
    )
    run_id = run_resp.json()["run_id"]

    approve_resp = await client.post(
        f"/api/v1/agent/{run_id}/approve",
        headers=headers,
        json={"edited_answers": {}},
    )
    application_id = approve_resp.json()["application_id"]

    application = await client.get(f"/api/v1/applications/{application_id}", headers=headers)
    assert application.json()["ats_platform"] == "greenhouse"
    assert application.json()["source_url"] == "https://boards.greenhouse.io/acme/jobs/123"


async def test_agent_reject_never_submits(client: AsyncClient) -> None:
    token = await _register_and_login(client, "agent3@test.com")
    await _upload_default_resume(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    run_resp = await client.post(
        "/api/v1/agent/run",
        headers=headers,
        json={"html": FORM_HTML, "job_description": JOB_DESCRIPTION},
    )
    run_id = run_resp.json()["run_id"]

    reject_resp = await client.post(
        f"/api/v1/agent/{run_id}/reject",
        headers=headers,
        json={"reason": "Not interested in this role"},
    )
    assert reject_resp.status_code == 200
    body = reject_resp.json()

    assert body["status"] == "completed"
    assert body["application_status"] != "submitted"

    if body["application_id"] is not None:
        application = await client.get(f"/api/v1/applications/{body['application_id']}", headers=headers)
        assert application.json()["status"] != "submitted"


async def test_agent_run_requires_default_resume(client: AsyncClient) -> None:
    token = await _register_and_login(client, "agent4@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/agent/run",
        headers=headers,
        json={"html": FORM_HTML, "job_description": JOB_DESCRIPTION},
    )
    assert resp.status_code == 422


async def test_agent_endpoints_require_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/agent/run",
        json={"html": FORM_HTML, "job_description": JOB_DESCRIPTION},
    )
    assert resp.status_code in (401, 403)
