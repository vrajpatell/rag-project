"""Hybrid sparse + dense indexer."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from rag_project.schemas.chunks import Chunk

logger = logging.getLogger(__name__)


class HybridIndexer:
    def __init__(
        self,
        sparse_index: LocalBM25Index,
        dense_index: FaissANNIndex,
        embed_fn,
    ) -> None:
        self.sparse = sparse_index
        self.dense = dense_index
        self.embed_fn = embed_fn

    def index_chunks(self, chunks: list[Chunk], mode: str = "incremental") -> dict[str, Any]:
        if not chunks:
            return {"indexed": 0}
        if mode == "rebuild":
            self.sparse.clear()
            self.dense.clear()

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        meta = [
            {
                "tenant_id": c.tenant_id,
                "collection_id": c.collection_id,
                "document_id": c.document_id,
                "source_uri": c.source_uri,
            }
            for c in chunks
        ]
        self.sparse.add_documents(ids, texts, meta)
        vectors = self.embed_fn(texts)
        if isinstance(vectors, list):
            vectors = np.array(vectors, dtype=np.float32)
        self.dense.add_vectors(ids, vectors, meta)
        return {"indexed": len(chunks), "chunk_ids": ids}

    def persist(self, sparse_path: str, dense_path: str) -> None:
        self.sparse.persist(sparse_path)
        self.dense.persist(dense_path)

    def load(self, sparse_path: str, dense_path: str) -> None:
        self.sparse.load(sparse_path)
        self.dense.load(dense_path)
