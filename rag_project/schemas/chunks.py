"""Chunk schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    tenant_id: str
    collection_id: str
    chunk_index: int
    text: str
    token_count: int = 0
    page_number: int | None = None
    section_title: str | None = None
    source_uri: str = ""
    content_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
