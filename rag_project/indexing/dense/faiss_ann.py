"""FAISS ANN index with Flat/HNSW support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


class FaissANNIndex:
    def clear(self) -> None:
        self.__init__(self.dim, self.index_type)

    def __init__(self, dim: int = 384, index_type: str = "flat") -> None:
        if faiss is None:
            raise RuntimeError("faiss is not installed")
        self.dim = dim
        self.index_type = index_type
        self.chunk_ids: list[str] = []
        self.metadata: list[dict[str, Any]] = []
        self.tenant_map: dict[str, str] = {}
        self.collection_map: dict[str, str] = {}
        self._id_to_idx: dict[str, int] = {}
        self.index = self._create_index()

    def _create_index(self):
        if self.index_type == "hnsw":
            index = faiss.IndexHNSWFlat(self.dim, 32)
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatL2(self.dim)
            index = faiss.IndexIVFFlat(quantizer, self.dim, min(100, max(1, 1)))
        else:
            index = faiss.IndexFlatL2(self.dim)
        return index

    def add_vectors(
        self,
        chunk_ids: list[str],
        vectors: np.ndarray,
        metadata: list[dict[str, Any]] | None = None,
    ) -> None:
        metadata = metadata or [{}] * len(chunk_ids)
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if self.index_type == "ivf" and not self.index.is_trained:
            if vectors.shape[0] >= 10:
                self.index.train(vectors)
        new_vectors: list[np.ndarray] = []
        for i, (cid, meta) in enumerate(zip(chunk_ids, metadata)):
            if cid in self._id_to_idx:
                continue
            self._id_to_idx[cid] = len(self.chunk_ids)
            self.chunk_ids.append(cid)
            self.metadata.append(meta)
            self.tenant_map[cid] = meta.get("tenant_id", "default")
            self.collection_map[cid] = meta.get("collection_id", "default")
            new_vectors.append(vectors[i])
        if new_vectors:
            batch = np.vstack(new_vectors).astype(np.float32)
            self.index.add(batch)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        tenant_id: str | None = None,
        collection_id: str | None = None,
    ) -> list[tuple[str, float]]:
        if self.index.ntotal == 0:
            return []
        q = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        k = min(top_k * 5, self.index.ntotal)
        dists, idxs = self.index.search(q, k)
        results: list[tuple[str, float]] = []
        for dist, idx in zip(dists[0], idxs[0]):
            if idx < 0 or idx >= len(self.chunk_ids):
                continue
            cid = self.chunk_ids[int(idx)]
            if tenant_id and self.tenant_map.get(cid) != tenant_id:
                continue
            if collection_id and self.collection_map.get(cid) != collection_id:
                continue
            score = 1.0 / (1.0 + float(dist))
            results.append((cid, score))
            if len(results) >= top_k:
                break
        return results

    def delete_by_chunk_ids(self, chunk_ids: list[str]) -> None:
        # FAISS lacks efficient delete; mark for rebuild
        remove = set(chunk_ids)
        keep = [i for i, cid in enumerate(self.chunk_ids) if cid not in remove]
        if len(keep) == len(self.chunk_ids):
            return
        # Full rebuild required - caller should re-index
        self.chunk_ids = [self.chunk_ids[i] for i in keep]
        self.metadata = [self.metadata[i] for i in keep]
        self._id_to_idx = {cid: i for i, cid in enumerate(self.chunk_ids)}
        self.tenant_map = {cid: self.tenant_map[cid] for cid in self.chunk_ids}
        self.collection_map = {cid: self.collection_map[cid] for cid in self.chunk_ids}

    def persist(self, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(p))
        manifest = {
            "chunk_ids": self.chunk_ids,
            "metadata": self.metadata,
            "tenant_map": self.tenant_map,
            "collection_map": self.collection_map,
            "dim": self.dim,
            "index_type": self.index_type,
        }
        p.with_suffix(".manifest.json").write_text(json.dumps(manifest))

    def load(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            return
        self.index = faiss.read_index(str(p))
        manifest_path = p.with_suffix(".manifest.json")
        if manifest_path.exists():
            m = json.loads(manifest_path.read_text())
            self.chunk_ids = m["chunk_ids"]
            self.metadata = m["metadata"]
            self.tenant_map = m.get("tenant_map", {})
            self.collection_map = m.get("collection_map", {})
            self.dim = m.get("dim", self.dim)
            self._id_to_idx = {cid: i for i, cid in enumerate(self.chunk_ids)}
