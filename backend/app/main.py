"""FastAPI application factory, lifespan, CORS, exception handlers, routers."""
from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, request_id_ctx

logger = logging.getLogger("app.main")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response


async def _build_checkpointer():
    """Builds the LangGraph checkpointer. Prefers a persistent SQLite-backed
    checkpointer; falls back to an in-memory checkpointer if the sqlite
    checkpoint package is unavailable (e.g. minimal test environments).
    """
    try:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        os.makedirs("./storage", exist_ok=True)
        cm = AsyncSqliteSaver.from_conn_string("./storage/checkpoints.db")
        saver = await cm.__aenter__()
        return saver, cm
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Falling back to in-memory LangGraph checkpointer: %s", exc)
        return MemorySaver(), None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging("DEBUG" if settings.DEBUG else "INFO")
    os.makedirs(settings.RESUME_STORAGE_DIR, exist_ok=True)
    os.makedirs(settings.SCREENSHOT_STORAGE_DIR, exist_ok=True)

    saver, cm = await _build_checkpointer()
    app.state.checkpointer = saver
    app.state._checkpointer_cm = cm

    logger.info("Application startup complete")
    yield

    if cm is not None:
        await cm.__aexit__(None, None, None)
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
