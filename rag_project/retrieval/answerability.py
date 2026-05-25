"""Answerability classifier."""

from __future__ import annotations

from dataclasses import dataclass
import re

from rag_project.retrieval.source_confidence import SourceConfidence
from rag_project.schemas.retrieval import RetrievalCandidate


@dataclass
class AnswerabilityResult:
    answerable: bool
    score: float
    reason: str
    missing_information: list[str]


class AnswerabilityClassifier:
    def __init__(self, min_score: float = 0.70, min_high_conf_chunks: int = 1) -> None:
        self.min_score = min_score
        self.min_high_conf_chunks = min_high_conf_chunks

    def classify(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        confidences: list[SourceConfidence],
    ) -> AnswerabilityResult:
        if not candidates:
            return AnswerabilityResult(
                answerable=False,
                score=0.0,
                reason="no_candidates",
                missing_information=["No retrieved context"],
            )
        q_terms = set(re.findall(r"\w+", query.lower()))
        high_conf = [c for c in confidences if c.score >= 0.65]
        coverage = 0.0
        for cand in candidates[:3]:
            text_terms = set(re.findall(r"\w+", cand.text.lower()))
            coverage = max(coverage, len(q_terms & text_terms) / max(len(q_terms), 1))
        max_conf = max((c.score for c in confidences), default=0.0)
        avg_conf = sum(c.score for c in confidences[:5]) / min(5, len(confidences))
        avg_rerank = sum((c.rerank_score or 0) for c in candidates[:5]) / min(5, len(candidates))
        score = 0.35 * max_conf + 0.25 * avg_conf + 0.25 * coverage + 0.15 * min(avg_rerank, 1.0)
        missing: list[str] = []
        if len(high_conf) < self.min_high_conf_chunks:
            missing.append("insufficient high-confidence sources")
        if coverage < 0.15:
            missing.append("low query term coverage in evidence")
        strong_evidence = max_conf >= 0.75 and coverage >= 0.1 and len(high_conf) >= self.min_high_conf_chunks
        answerable = (
            score >= self.min_score or strong_evidence
        ) and len(high_conf) >= self.min_high_conf_chunks and coverage >= 0.1
        reason = "sufficient_evidence" if answerable else "insufficient_evidence"
        return AnswerabilityResult(
            answerable=answerable,
            score=score,
            reason=reason,
            missing_information=missing,
        )
