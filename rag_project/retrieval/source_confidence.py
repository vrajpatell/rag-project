"""Source confidence scoring."""

from __future__ import annotations

from dataclasses import dataclass, field

from rag_project.schemas.retrieval import RetrievalCandidate


@dataclass
class SourceConfidence:
    chunk_id: str
    score: float
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SourceConfidenceScorer:
    def score(self, query: str, candidates: list[RetrievalCandidate]) -> list[SourceConfidence]:
        results: list[SourceConfidence] = []
        for c in candidates:
            rerank = c.rerank_score or c.hybrid_score
            score = 0.4 * min(rerank, 1.0) + 0.3 * min(c.dense_score, 1.0) + 0.2 * min(c.sparse_score / max(c.sparse_score, 1), 1.0) if c.sparse_score else 0.1
            score = min(1.0, max(0.0, score + 0.1))
            reasons = [f"rerank={rerank:.3f}", f"hybrid={c.hybrid_score:.3f}"]
            warnings: list[str] = []
            parser_q = c.metadata.get("parser_quality", 1.0)
            if isinstance(parser_q, (int, float)) and parser_q < 0.5:
                score *= 0.8
                warnings.append("low_parser_quality")
            if len(c.text) < 50:
                score *= 0.7
                warnings.append("short_chunk")
            results.append(SourceConfidence(chunk_id=c.chunk_id, score=score, reasons=reasons, warnings=warnings))
        return results
