"""Batch embedding with retry and cache."""

from __future__ import annotations

import logging
import time
from typing import Callable

from rag_project.core.hashing import content_hash
from rag_project.schemas.chunks import Chunk

logger = logging.getLogger(__name__)


class BatchEmbedder:
    def __init__(
        self,
        provider,
        batch_size: int = 128,
        cache: dict[str, list[float]] | None = None,
        max_retries: int = 3,
    ) -> None:
        self.provider = provider
        self.batch_size = batch_size
        self.cache = cache if cache is not None else {}
        self.max_retries = max_retries

    def embed_chunks(self, chunks: list[Chunk], skip_hashes: set[str] | None = None) -> dict[str, list[float]]:
        skip_hashes = skip_hashes or set()
        result: dict[str, list[float]] = {}
        pending: list[Chunk] = []
        for ch in chunks:
            key = content_hash(ch.text)
            if ch.content_hash in skip_hashes or key in self.cache:
                result[ch.chunk_id] = self.cache.get(key, self.cache.get(ch.content_hash, []))
                continue
            pending.append(ch)

        for i in range(0, len(pending), self.batch_size):
            batch = pending[i : i + self.batch_size]
            texts = [c.text for c in batch]
            vectors = self._embed_with_retry(texts)
            for ch, vec in zip(batch, vectors):
                h = content_hash(ch.text)
                self.cache[h] = vec
                result[ch.chunk_id] = vec
        return result

    def _embed_with_retry(self, texts: list[str]) -> list[list[float]]:
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                return self.provider.embed(texts)
            except Exception as e:
                last_err = e
                logger.warning("Embed attempt %s failed: %s", attempt + 1, e)
                time.sleep(2**attempt)
        raise last_err or RuntimeError("Embedding failed")
