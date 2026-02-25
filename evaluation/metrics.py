"""Basic evaluation metrics for retrieval systems."""

from typing import List, Sequence


def precision_at_k(relevances: List[Sequence[int]], k: int = 5) -> float:
    """Compute precision at K across multiple queries."""
    precisions = []
    for rel in relevances:
        if not rel:
            precisions.append(0.0)
        else:
            precisions.append(sum(rel[:k]) / k)
    return sum(precisions) / len(precisions) if precisions else 0.0


def mean_reciprocal_rank(relevances: List[Sequence[int]]) -> float:
    """Compute MRR across multiple queries."""
    scores = []
    for rel in relevances:
        rank = next((i + 1 for i, r in enumerate(rel) if r), 0)
        scores.append(1 / rank if rank else 0.0)
    return sum(scores) / len(scores) if scores else 0.0
