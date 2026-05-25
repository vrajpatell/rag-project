"""Evaluation metrics."""

from __future__ import annotations


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top = retrieved[:k]
    if not top:
        return 0.0
    return len([r for r in top if r in relevant]) / len(top)


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top = retrieved[:k]
    return len([r for r in top if r in relevant]) / len(relevant)


def mrr(retrieved: list[str], relevant: set[str]) -> float:
    for i, r in enumerate(retrieved, 1):
        if r in relevant:
            return 1.0 / i
    return 0.0


def hit_rate(retrieved: list[str], relevant: set[str], k: int) -> float:
    top = set(retrieved[:k])
    return 1.0 if top & relevant else 0.0
