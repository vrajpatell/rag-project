"""Optional reranking of retrieved results."""

from typing import List, Dict


def rerank_by_recency(results: List[Dict], recency_bias: bool = True) -> List[Dict]:
    """Sort results by score; apply recency bias if enabled."""
    # In this stub we simply return the results sorted by score ascending
    return sorted(results, key=lambda r: r["score"])