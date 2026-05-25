"""Local BM25 index."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class LocalBM25Index:
    def clear(self) -> None:
        self.__init__()

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.chunk_ids: list[str] = []
        self.texts: list[str] = []
        self.metadata: list[dict[str, Any]] = []
        self.doc_freq: Counter[str] = Counter()
        self.term_freqs: list[Counter[str]] = []
        self.doc_lens: list[int] = []
        self.avgdl = 0.0
        self.tenant_map: dict[str, str] = {}
        self.collection_map: dict[str, str] = {}

    def add_documents(
        self,
        chunk_ids: list[str],
        texts: list[str],
        metadata: list[dict[str, Any]] | None = None,
    ) -> None:
        metadata = metadata or [{}] * len(texts)
        for cid, text, meta in zip(chunk_ids, texts, metadata):
            if cid in self.chunk_ids:
                continue
            tokens = _tokenize(text)
            tf = Counter(tokens)
            self.chunk_ids.append(cid)
            self.texts.append(text)
            self.metadata.append(meta)
            self.term_freqs.append(tf)
            self.doc_lens.append(len(tokens))
            self.tenant_map[cid] = meta.get("tenant_id", "default")
            self.collection_map[cid] = meta.get("collection_id", "default")
            for t in set(tokens):
                self.doc_freq[t] += 1
        n = len(self.doc_lens)
        self.avgdl = sum(self.doc_lens) / n if n else 0.0

    def _score(self, query_tokens: list[str], idx: int) -> float:
        tf = self.term_freqs[idx]
        dl = self.doc_lens[idx]
        score = 0.0
        n = len(self.chunk_ids)
        for term in query_tokens:
            if term not in self.doc_freq:
                continue
            df = self.doc_freq[term]
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
            freq = tf.get(term, 0)
            denom = freq + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1))
            score += idf * (freq * (self.k1 + 1)) / max(denom, 1e-9)
        return score

    def search(
        self,
        query: str,
        top_k: int,
        tenant_id: str | None = None,
        collection_id: str | None = None,
    ) -> list[tuple[str, float]]:
        q_tokens = _tokenize(query)
        scores: list[tuple[str, float]] = []
        for i, cid in enumerate(self.chunk_ids):
            if tenant_id and self.tenant_map.get(cid) != tenant_id:
                continue
            if collection_id and self.collection_map.get(cid) != collection_id:
                continue
            s = self._score(q_tokens, i)
            if s > 0:
                scores.append((cid, s))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def delete_by_chunk_ids(self, chunk_ids: list[str]) -> None:
        remove = set(chunk_ids)
        indices = [i for i, cid in enumerate(self.chunk_ids) if cid not in remove]
        self._rebuild_at_indices(indices)

    def _rebuild_at_indices(self, indices: list[int]) -> None:
        self.chunk_ids = [self.chunk_ids[i] for i in indices]
        self.texts = [self.texts[i] for i in indices]
        self.metadata = [self.metadata[i] for i in indices]
        self.term_freqs = [self.term_freqs[i] for i in indices]
        self.doc_lens = [self.doc_lens[i] for i in indices]
        self.doc_freq = Counter()
        for tf in self.term_freqs:
            for t in set(tf):
                self.doc_freq[t] += 1
        n = len(self.doc_lens)
        self.avgdl = sum(self.doc_lens) / n if n else 0.0

    def persist(self, path: str) -> None:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        data = {
            "chunk_ids": self.chunk_ids,
            "texts": self.texts,
            "metadata": self.metadata,
            "tenant_map": self.tenant_map,
            "collection_map": self.collection_map,
        }
        (p / "bm25.json").write_text(json.dumps(data))

    def load(self, path: str) -> None:
        p = Path(path) / "bm25.json"
        if not p.exists():
            return
        data = json.loads(p.read_text())
        self.chunk_ids = data["chunk_ids"]
        self.texts = data["texts"]
        self.metadata = data["metadata"]
        self.tenant_map = data.get("tenant_map", {})
        self.collection_map = data.get("collection_map", {})
        self.term_freqs = [_tokenize(t) for t in self.texts]
        self.term_freqs = [Counter(t) for t in self.term_freqs]
        self.doc_lens = [len(tf) for tf in self.term_freqs]
        self.doc_freq = Counter()
        for tf in self.term_freqs:
            for t in set(tf):
                self.doc_freq[t] += 1
        n = len(self.doc_lens)
        self.avgdl = sum(self.doc_lens) / n if n else 0.0
