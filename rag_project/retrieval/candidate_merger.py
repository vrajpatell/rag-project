"""Merge sparse and dense retrieval candidates."""

from __future__ import annotations


def normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []
    mn, mx = min(scores), max(scores)
    if mx == mn:
        return [1.0 if s > 0 else 0.0 for s in scores]
    return [(s - mn) / (mx - mn) for s in scores]


def merge_candidates(
    sparse: list[tuple[str, float]],
    dense: list[tuple[str, float]],
    sparse_weight: float = 0.45,
    dense_weight: float = 0.55,
) -> dict[str, float]:
    sparse_map = {cid: s for cid, s in sparse}
    dense_map = {cid: s for cid, s in dense}
    all_ids = set(sparse_map) | set(dense_map)
    sp_norm = normalize_scores([sparse_map.get(i, 0.0) for i in all_ids])
    dn_norm = normalize_scores([dense_map.get(i, 0.0) for i in all_ids])
    merged: dict[str, float] = {}
    for i, cid in enumerate(all_ids):
        merged[cid] = sparse_weight * sp_norm[i] + dense_weight * dn_norm[i]
    return merged
