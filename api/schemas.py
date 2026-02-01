"""Pydantic schemas for the RAG API."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class RAGRequest(BaseModel):
    query: str = Field(..., description="The natural language query.")
    top_k: int = Field(8, description="Number of contexts to retrieve.")
    use_rerank: bool = Field(True, description="Whether to apply reranking.")


class ContextChunk(BaseModel):
    doc_id: int
    section: str | None = None
    text: str
    score: float
    meta: Dict[str, Any] = {}


class RAGResponse(BaseModel):
    query: str
    retrieved_contexts: List[Dict[str, Any]]
    synthesized_answer: str
    confidence_score: float
    citations: List[str]