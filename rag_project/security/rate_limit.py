"""Simple in-memory rate limiter."""

from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, per_minute: int = 60) -> None:
        self.per_minute = per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.time()
        window = now - 60
        self._hits[key] = [t for t in self._hits[key] if t > window]
        if len(self._hits[key]) >= self.per_minute:
            return False
        self._hits[key].append(now)
        return True
