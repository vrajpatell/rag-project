"""Authentication helpers."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request

from rag_project.core.config import Settings


def verify_api_key(
    request: Request,
    settings: Settings,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    if settings.auth_mode == "none":
        return "anonymous"
    keys = settings.get_api_key_set()
    if not keys:
        return "anonymous"
    key = x_api_key or request.headers.get("Authorization", "").replace("Bearer ", "")
    if key not in keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key
