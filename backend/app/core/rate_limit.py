"""Simple Redis-backed sliding-window rate limiter as a FastAPI dependency."""
from __future__ import annotations

import time
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Request

from app.core.config import settings
from app.core.exceptions import RateLimitError

_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


class RateLimiter:
    """Fixed-window rate limiter keyed by client IP + route."""

    def __init__(self, times: int = settings.RATE_LIMIT_PER_MINUTE, window_seconds: int = 60) -> None:
        self.times = times
        self.window_seconds = window_seconds

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        window = int(time.time() // self.window_seconds)
        key = f"ratelimit:{request.url.path}:{client_ip}:{window}"

        try:
            redis_client = get_redis()
            count = await redis_client.incr(key)
            if count == 1:
                await redis_client.expire(key, self.window_seconds)
            if count > self.times:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
        except RateLimitError:
            raise
        except Exception:
            # Redis unavailable — fail open rather than blocking the API.
            return
