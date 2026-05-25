"""Security-related schemas."""

from __future__ import annotations

from pydantic import BaseModel


class TenantContext(BaseModel):
    tenant_id: str
    collection_ids: list[str]
    roles: list[str] = []
