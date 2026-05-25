"""Evaluation schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GoldenExample(BaseModel):
    query: str
    expected_answer: str = ""
    relevant_chunk_ids: list[str] = Field(default_factory=list)
    required_citations: list[str] = Field(default_factory=list)
    tenant_id: str = "default"
    collection_id: str = "default"
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalReport(BaseModel):
    dataset_path: str
    total_examples: int
    metrics: dict[str, float]
    failures: list[dict[str, Any]] = Field(default_factory=list)
    passed_regression_gate: bool = True
