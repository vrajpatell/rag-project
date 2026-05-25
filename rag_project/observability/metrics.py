"""Prometheus metrics."""

from __future__ import annotations

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

    RAG_REQUESTS = Counter("rag_requests_total", "Total RAG requests")
    RAG_LATENCY = Histogram("rag_request_latency_seconds", "RAG request latency")
    RAG_RETRIEVAL_LATENCY = Histogram("rag_retrieval_latency_seconds", "Retrieval latency")
    RAG_GENERATION_LATENCY = Histogram("rag_generation_latency_seconds", "Generation latency")
    RAG_ABSTENTIONS = Counter("rag_abstentions_total", "Abstentions")
    RAG_CITATION_FAILURES = Counter("rag_citation_validation_failures_total", "Citation failures")
    RAG_CACHE_HITS = Counter("rag_cache_hits_total", "Cache hits")
    RAG_CACHE_MISSES = Counter("rag_cache_misses_total", "Cache misses")
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


def metrics_response() -> tuple[bytes, str]:
    if not PROMETHEUS_AVAILABLE:
        return b"# prometheus_client not installed\n", "text/plain"
    return generate_latest(), CONTENT_TYPE_LATEST
