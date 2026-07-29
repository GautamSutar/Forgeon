from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_and_login(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "secret123", "full_name": "Ada Lovelace"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "a@b.com"

    resp = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "secret123"})
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


async def test_register_duplicate_email_conflicts(client: AsyncClient) -> None:
    payload = {"email": "dup@b.com", "password": "secret123", "full_name": "Dup User"}
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "c@d.com", "password": "correct-pass", "full_name": "C D"},
    )
    resp = await client.post("/api/v1/auth/login", json={"email": "c@d.com", "password": "wrong"})
    assert resp.status_code == 401


async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)


async def test_me_with_token(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "e@f.com", "password": "secret123", "full_name": "E F"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": "e@f.com", "password": "secret123"})
    token = login.json()["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "e@f.com"


async def test_refresh_token(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "g@h.com", "password": "secret123", "full_name": "G H"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": "g@h.com", "password": "secret123"})
    refresh_token = login.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
