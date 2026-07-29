from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.pdf_helper import build_pdf

pytestmark = pytest.mark.asyncio


async def _register_and_login(client: AsyncClient, email: str = "app@test.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "App User"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return login.json()["access_token"]


async def _upload_resume(client: AsyncClient, token: str) -> str:
    resp = await client.post(
        "/api/v1/resumes/upload",
        headers={"Authorization": f"Bearer {token}"},
        params={"set_default": True},
        files={"file": ("resume.pdf", build_pdf(["Jane Doe"]), "application/pdf")},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_create_and_get_application(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resume_id = await _upload_resume(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post(
        "/api/v1/applications",
        headers=headers,
        json={"resume_id": resume_id, "role_title": "Backend Engineer", "ats_platform": "greenhouse"},
    )
    assert create.status_code == 201
    body = create.json()
    assert body["role_title"] == "Backend Engineer"
    assert body["status"] == "draft"

    got = await client.get(f"/api/v1/applications/{body['id']}", headers=headers)
    assert got.status_code == 200
    assert got.json()["id"] == body["id"]


async def test_list_update_and_delete_application(client: AsyncClient) -> None:
    token = await _register_and_login(client, "app2@test.com")
    resume_id = await _upload_resume(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    created = (
        await client.post(
            "/api/v1/applications",
            headers=headers,
            json={"resume_id": resume_id, "role_title": "Data Engineer"},
        )
    ).json()

    listed = await client.get("/api/v1/applications", headers=headers)
    assert listed.status_code == 200
    assert any(a["id"] == created["id"] for a in listed.json())

    updated = await client.patch(
        f"/api/v1/applications/{created['id']}",
        headers=headers,
        json={"status": "submitted"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "submitted"

    deleted = await client.delete(f"/api/v1/applications/{created['id']}", headers=headers)
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/applications/{created['id']}", headers=headers)
    assert missing.status_code == 404


async def test_application_not_visible_to_other_user(client: AsyncClient) -> None:
    token_a = await _register_and_login(client, "owner@test.com")
    resume_id = await _upload_resume(client, token_a)
    created = (
        await client.post(
            "/api/v1/applications",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"resume_id": resume_id, "role_title": "SRE"},
        )
    ).json()

    token_b = await _register_and_login(client, "other@test.com")
    resp = await client.get(
        f"/api/v1/applications/{created['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


async def test_applications_require_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/applications")
    assert resp.status_code in (401, 403)
