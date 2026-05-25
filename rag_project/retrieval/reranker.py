"""Two-stage reranking."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from rag_project.schemas.retrieval import RetrievalCandidate


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, candidates: list[RetrievalCandidate], top_k: int) -> list[RetrievalCandidate]: ...


class HeuristicReranker(Reranker):
    def rerank(self, query: str, candidates: list[RetrievalCandidate], top_k: int) -> list[RetrievalCandidate]:
        q_terms = set(re.findall(r"\w+", query.lower()))
        seen_docs: set[str] = set()
        scored: list[tuple[RetrievalCandidate, float, str]] = []
        for c in candidates:
            text_terms = set(re.findall(r"\w+", c.text.lower()))
            overlap = len(q_terms & text_terms) / max(len(q_terms), 1)
            base = c.hybrid_score
            dup_penalty = 0.15 if c.document_id in seen_docs else 0.0
            seen_docs.add(c.document_id)
            score = 0.6 * base + 0.3 * overlap + 0.1 * c.dense_score - dup_penalty
            explanation = f"hybrid={base:.3f}, kw_overlap={overlap:.3f}"
            scored.append((c, score, explanation))
        scored.sort(key=lambda x: x[1], reverse=True)
        out: list[RetrievalCandidate] = []
        for c, score, expl in scored[:top_k]:
            updated = c.model_copy(update={"rerank_score": score, "rerank_explanation": expl})
            out.append(updated)
        return out
