"""In-memory cache with tenant isolation."""

from __future__ import annotations

import time
from typing import Any

from rag_project.core.hashing import cache_key_parts
from rag_project.cache.cache_base import CacheBase


class MemoryCache(CacheBase):
    def __init__(self, ttl: int = 3600) -> None:
        self.ttl = ttl
        self._store: dict[str, tuple[Any, float]] = {}

    def _key(self, *parts: str) -> str:
        return cache_key_parts(*parts)

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if not entry:
            return None
        value, expires = entry
        if time.time() > expires:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires = time.time() + (ttl or self.ttl)
        self._store[key] = (value, expires)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def get_query_response(
        self, tenant_id: str, collection_ids: list[str], query: str, filters: dict
    ) -> dict | None:
        key = self._key("query", tenant_id, ",".join(collection_ids), query, str(sorted(filters.items())))
        return self.get(key)

    def set_query_response(
        self, tenant_id: str, collection_ids: list[str], query: str, filters: dict, value: dict
    ) -> None:
        key = self._key("query", tenant_id, ",".join(collection_ids), query, str(sorted(filters.items())))
        self.set(key, value)
