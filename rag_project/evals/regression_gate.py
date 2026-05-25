"""CI regression gate thresholds."""

from __future__ import annotations

DEFAULT_THRESHOLDS = {
    "hit_rate": 0.0,
    "mrr": 0.0,
    "abstention_precision": 0.5,
}


def check_regression(metrics: dict[str, float], thresholds: dict[str, float] | None = None) -> bool:
    thresholds = thresholds or DEFAULT_THRESHOLDS
    for key, min_val in thresholds.items():
        if metrics.get(key, 0) < min_val:
            return False
    return True
