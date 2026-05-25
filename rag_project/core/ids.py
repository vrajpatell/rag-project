"""ID generation utilities."""

from __future__ import annotations

import uuid


def new_id(prefix: str = "") -> str:
    uid = uuid.uuid4().hex
    return f"{prefix}{uid}" if prefix else uid


def chunk_id(document_id: str, chunk_index: int, content_hash: str) -> str:
    short = content_hash[:12]
    return f"chk_{document_id}_{chunk_index}_{short}"


def document_id_from_hash(content_hash: str, tenant_id: str, collection_id: str) -> str:
    return f"doc_{tenant_id}_{collection_id}_{content_hash[:16]}"


def job_id() -> str:
    return new_id("job_")
