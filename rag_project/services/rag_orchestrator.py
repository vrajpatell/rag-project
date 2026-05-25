"""End-to-end RAG orchestration."""

from __future__ import annotations

import logging
import time
from typing import Any

from rag_project.core.ids import new_id
from rag_project.generation.citation_validator import CitationValidator
from rag_project.generation.claim_verifier import ClaimVerifier
from rag_project.generation.constrained_generator import ConstrainedGenerator
from rag_project.generation.fallback import (
    ABSTAIN_MESSAGE,
    build_abstain_response,
    build_citations_from_candidates,
)
from rag_project.retrieval.answerability import AnswerabilityClassifier
from rag_project.retrieval.source_confidence import SourceConfidenceScorer
from rag_project.schemas.api import RAGQueryRequest, RAGQueryResponse
from rag_project.schemas.generation import CitedClaim

logger = logging.getLogger(__name__)


class HallucinationGuard:
    def __init__(self) -> None:
        self.citation_validator = CitationValidator()
        self.claim_verifier = ClaimVerifier()

    def run(
        self,
        query: str,
        generated,
        candidates,
        citations,
        citation_map,
        citation_id_set: set[str],
    ) -> tuple[bool, list[str]]:
        warnings: list[str] = []
        cv = self.citation_validator.validate(generated, citations, citation_id_set)
        if not cv.valid:
            warnings.extend(cv.warnings)
            warnings.append("citation_validation_failed")
            return False, warnings
        chunk_map = {v: k for k, v in citation_map.items()}
        pv = self.claim_verifier.verify(generated, candidates, {c.citation_id: c.chunk_id for c in citations})
        if not pv.supported:
            warnings.append(f"unsupported_claims: {pv.unsupported_claims[:3]}")
            return False, warnings
        return True, warnings


class RAGOrchestrator:
    def __init__(
        self,
        retriever,
        reranker,
        generator: ConstrainedGenerator,
        settings,
        cache=None,
        metrics=None,
    ) -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.generator = generator
        self.settings = settings
        self.cache = cache
        self.metrics = metrics
        self.confidence_scorer = SourceConfidenceScorer()
        self.answerability = AnswerabilityClassifier(
            min_score=settings.rag_min_answerability_score
        )
        self.guard = HallucinationGuard()

    def _build_citation_map(self, candidates) -> dict[str, str]:
        return {c.chunk_id: f"C{i+1}" for i, c in enumerate(candidates)}

    def query(self, request: RAGQueryRequest) -> RAGQueryResponse:
        trace_id = new_id("trace_")
        t0 = time.perf_counter()
        tenant_id = request.tenant_id
        collection_ids = request.collection_ids

        if self.cache:
            cached = self.cache.get_query_response(
                tenant_id, collection_ids, request.query, request.filters
            )
            if cached:
                return RAGQueryResponse.model_validate(cached)

        candidates = self.retriever.retrieve(
            request.query,
            tenant_id,
            collection_ids,
            top_k=self.settings.rag_retrieval_candidates,
            filters=request.filters,
        )
        reranked = self.reranker.rerank(
            request.query, candidates, top_k=request.top_k or self.settings.rag_rerank_top_k
        )
        confidences = self.confidence_scorer.score(request.query, reranked)
        conf_map = {c.chunk_id: c for c in confidences}

        min_conf = self.settings.rag_min_source_confidence
        if confidences and all(c.score < min_conf for c in confidences):
            if request.allow_abstention:
                return build_abstain_response(
                    "Retrieved evidence did not meet source confidence thresholds.",
                    trace_id,
                )

        ans_result = self.answerability.classify(request.query, reranked, confidences)
        if not ans_result.answerable and request.allow_abstention:
            return build_abstain_response(
                f"Answerability check failed: {ans_result.reason}. " + "; ".join(ans_result.missing_information),
                trace_id,
            )

        citation_map = self._build_citation_map(reranked)
        generated = self.generator.generate(request.query, reranked, citation_map)

        if generated.abstained and request.allow_abstention:
            return build_abstain_response(
                generated.abstention_reason or "Model abstained",
                trace_id,
            )

        citations = build_citations_from_candidates(reranked, citation_map)
        citation_id_set = set(citation_map.values())

        ok, guard_warnings = self.guard.run(
            request.query, generated, reranked, citations, citation_map, citation_id_set
        )
        if not ok and request.allow_abstention:
            return build_abstain_response(
                "Retrieved evidence did not meet answerability and citation confidence thresholds.",
                trace_id,
                guard_warnings,
            )

        avg_conf = sum(c.score for c in confidences[:3]) / max(1, min(3, len(confidences)))
        final_conf = 0.6 * generated.confidence_score + 0.4 * avg_conf

        response = RAGQueryResponse(
            answer=generated.answer,
            abstained=False,
            confidence_score=round(final_conf, 3),
            citations=citations,
            cited_claims=generated.cited_claims,
            warnings=guard_warnings + generated.limitations,
            trace_id=trace_id,
        )

        if request.include_debug:
            response.debug = {
                "candidates": [c.model_dump() for c in reranked[:10]],
                "answerability": ans_result.__dict__,
                "confidences": [c.__dict__ for c in confidences[:10]],
            }

        if self.cache:
            self.cache.set_query_response(
                tenant_id, collection_ids, request.query, request.filters, response.model_dump()
            )

        elapsed = time.perf_counter() - t0
        logger.info("RAG query completed", extra={"trace_id": trace_id, "latency_s": elapsed})
        return response
