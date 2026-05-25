"""Document schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SourceType = Literal["local_file", "url", "api", "object_store"]


class DocumentSource(BaseModel):
    source_type: SourceType
    uri: str
    tenant_id: str = "default"
    collection_id: str = "default"
    metadata: dict[str, Any] = Field(default_factory=dict)


class RawDocument(BaseModel):
    raw_doc_id: str
    source: DocumentSource
    content_bytes: bytes | None = None
    content_text: str | None = None
    content_type: str = "text/plain"
    checksum: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedDocument(BaseModel):
    document_id: str
    tenant_id: str
    collection_id: str
    title: str = ""
    normalized_text: str
    source_uri: str
    content_hash: str
    simhash: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
