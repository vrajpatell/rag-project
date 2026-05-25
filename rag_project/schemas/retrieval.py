"""Retrieval schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str
    tenant_id: str = "default"
    collection_ids: list[str] = Field(default_factory=lambda: ["default"])
    top_k: int = 8
    filters: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None
    require_citations: bool = True
    allow_abstention: bool = True
    include_debug: bool = False


class RetrievalCandidate(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    source_uri: str = ""
    page_number: int | None = None
    section_title: str | None = None
    sparse_score: float = 0.0
    dense_score: float = 0.0
    hybrid_score: float = 0.0
    rerank_score: float | None = None
    rerank_explanation: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
