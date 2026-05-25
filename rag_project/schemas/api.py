"""API request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from rag_project.schemas.citations import Citation
from rag_project.schemas.generation import CitedClaim


class RAGQueryRequest(BaseModel):
    tenant_id: str = "default"
    collection_ids: list[str] = Field(default_factory=lambda: ["default"])
    query: str
    top_k: int = 8
    filters: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None
    require_citations: bool = True
    allow_abstention: bool = True
    include_debug: bool = False


class RAGQueryResponse(BaseModel):
    answer: str
    abstained: bool = False
    abstention_reason: str | None = None
    confidence_score: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    cited_claims: list[CitedClaim] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    trace_id: str = ""
    debug: dict[str, Any] | None = None


class IngestRequest(BaseModel):
    tenant_id: str = "default"
    collection_id: str = "default"
    source_path: str
    source_type: str = "local_file"


class IngestResponse(BaseModel):
    job_id: str
    status: str
    summary: dict[str, Any] = Field(default_factory=dict)


class JobStatusResponse(BaseModel):
    job_id: str
    job_type: str
    tenant_id: str
    collection_id: str
    status: str
    progress: float = 0.0
    error: str | None = None
    result: dict[str, Any] | None = None
