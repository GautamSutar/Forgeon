from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import agent, applications, auth, profiles, resumes, saved_answers

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(resumes.router)
api_router.include_router(applications.router)
api_router.include_router(saved_answers.router)
api_router.include_router(agent.router)
