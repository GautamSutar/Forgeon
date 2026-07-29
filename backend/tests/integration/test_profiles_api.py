from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _register_and_login(client: AsyncClient, email: str = "profile@test.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Profile User"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return login.json()["access_token"]


async def test_get_profile_creates_if_missing(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await client.get("/api/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["phone"] is None


async def test_profile_full_name_seeded_from_account_on_first_access(client: AsyncClient) -> None:
    """Regression test: a real complaint — the profile never had a name
    field at all, so agent-generated answers couldn't fill in "Full Name"
    even though the user gave their name at registration. A newly created
    profile must be seeded with the account's full_name automatically."""
    token = await _register_and_login(client, "profile-name@test.com")
    resp = await client.get("/api/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Profile User"


async def test_profile_full_name_editable_independent_of_account_name(client: AsyncClient) -> None:
    token = await _register_and_login(client, "profile-name2@test.com")
    resp = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Preferred Display Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Preferred Display Name"


async def test_update_profile(client: AsyncClient) -> None:
    token = await _register_and_login(client, "profile2@test.com")
    resp = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"location": "Remote", "years_experience": 5, "preferred_roles": ["Backend Engineer"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["location"] == "Remote"
    assert body["years_experience"] == 5
    assert body["preferred_roles"] == ["Backend Engineer"]


async def test_profile_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/profiles/me")
    assert resp.status_code in (401, 403)


async def test_update_profile_expanded_fields(client: AsyncClient) -> None:
    token = await _register_and_login(client, "profile-expanded@test.com")
    resp = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "headline": "Aspiring AI / Backend Developer",
            "current_company": "Globex Analytics",
            "current_job_title": "AI Intern",
            "university": "Example Institute of Technology, Metropolis",
            "highest_education": "B.Tech",
            "graduation_year": 2026,
            "willing_to_relocate": True,
            "remote_preference": "Remote",
            "availability": "Immediate",
            "languages_spoken": ["English", "Hindi"],
            "certifications": ["AWS Certified Solutions Architect"],
            "cover_letter": "I am excited to apply...",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["current_company"] == "Globex Analytics"
    assert body["university"] == "Example Institute of Technology, Metropolis"
    assert body["graduation_year"] == 2026
    assert body["willing_to_relocate"] is True
    assert body["languages_spoken"] == ["English", "Hindi"]
    assert body["certifications"] == ["AWS Certified Solutions Architect"]


async def test_update_profile_broad_field_set(client: AsyncClient) -> None:
    """Representative sample across personal/contact/education/experience/
    work-authorization/diversity/availability — not exhaustive over all ~47
    new fields, but covers one from each category to catch schema/model
    mismatches broadly."""
    token = await _register_and_login(client, "profile-broad@test.com")
    resp = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Jordan",
            "last_name": "Rivera",
            "gender": "Male",
            "date_of_birth": "2003-01-01",
            "nationality": "Indian",
            "city": "Metropolis",
            "country": "India",
            "postal_code": "100001",
            "employment_type": "Full-time",
            "kaggle_url": "https://kaggle.com/jordanrivera",
            "leetcode_url": "https://leetcode.com/jordanrivera",
            "degree": "B.Tech",
            "specialization": "Computer Science",
            "current_cgpa": 8.1,
            "tenth_percentage": 96.33,
            "twelfth_percentage": 90.0,
            "is_fresher": True,
            "work_authorized": True,
            "requires_visa_sponsorship": False,
            "citizenship": "Indian",
            "disability_status": "No",
            "veteran_status": "Not applicable",
            "immediate_joiner": True,
            "time_zone": "Asia/Kolkata",
            "awards": ["Hackworld Runner-Up"],
            "publications": [],
            "hobbies_interests": ["Chess"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["first_name"] == "Jordan"
    assert body["city"] == "Metropolis"
    assert body["degree"] == "B.Tech"
    assert body["current_cgpa"] == 8.1
    assert body["is_fresher"] is True
    assert body["work_authorized"] is True
    assert body["requires_visa_sponsorship"] is False
    assert body["awards"] == ["Hackworld Runner-Up"]
    assert body["hobbies_interests"] == ["Chess"]


async def test_update_profile_structured_work_experience_and_education(client: AsyncClient) -> None:
    """Workday-style "Add Another" multi-entry sections — a list of
    structured work experience / education entries, not a single flat
    field."""
    token = await _register_and_login(client, "profile-history@test.com")
    resp = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "work_experience": [
                {
                    "job_title": "AI Intern",
                    "company": "Globex Analytics",
                    "location": "Remote",
                    "is_current": True,
                    "start_month": 12,
                    "start_year": 2025,
                    "end_month": 3,
                    "end_year": 2026,
                    "description": "Built ML models for visa processing time prediction.",
                },
                {
                    "job_title": "Python Developer Intern",
                    "company": "Initech Solutions",
                    "is_current": False,
                    "start_month": 7,
                    "start_year": 2025,
                    "end_month": 9,
                    "end_year": 2025,
                },
            ],
            "education_history": [
                {"school": "Example Institute of Technology", "degree": "B.Tech", "gpa": "8.1", "end_year": 2026},
                {"school": "Pink Flower H.S. School", "gpa": "90", "end_year": 2022},
            ],
            "skills": ["Python", "FastAPI", "LangGraph"],
            "websites": ["https://example.com/portfolio-alt"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert len(body["work_experience"]) == 2
    assert body["work_experience"][0]["job_title"] == "AI Intern"
    assert body["work_experience"][0]["company"] == "Globex Analytics"
    assert body["work_experience"][0]["is_current"] is True
    assert body["work_experience"][1]["end_year"] == 2025

    assert len(body["education_history"]) == 2
    assert body["education_history"][0]["school"] == "Example Institute of Technology"
    assert body["education_history"][0]["gpa"] == "8.1"

    assert body["skills"] == ["Python", "FastAPI", "LangGraph"]
    assert body["websites"] == ["https://example.com/portfolio-alt"]


async def test_update_profile_rejects_malformed_work_experience(client: AsyncClient) -> None:
    """job_title and company are required per entry — this isn't a free-form
    blob, it's validated structured data."""
    token = await _register_and_login(client, "profile-history-invalid@test.com")
    resp = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"work_experience": [{"company": "Missing Job Title Co"}]},
    )
    assert resp.status_code == 422
