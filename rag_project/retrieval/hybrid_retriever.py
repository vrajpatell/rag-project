"""Hybrid BM25 + dense retriever."""

from __future__ import annotations

from typing import Any

import numpy as np

from rag_project.retrieval.candidate_merger import merge_candidates
from rag_project.retrieval.query_preprocessor import preprocess_query
from rag_project.schemas.retrieval import RetrievalCandidate


class HybridRetriever:
    def __init__(
        self,
        sparse_index,
        dense_index,
        document_store,
        embed_fn,
        sparse_weight: float = 0.45,
        dense_weight: float = 0.55,
    ) -> None:
        self.sparse = sparse_index
        self.dense = dense_index
        self.document_store = document_store
        self.embed_fn = embed_fn
        self.sparse_weight = sparse_weight
        self.dense_weight = dense_weight

    def retrieve(
        self,
        query: str,
        tenant_id: str,
        collection_ids: list[str],
        top_k: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalCandidate]:
        q = preprocess_query(query)
        collection_id = collection_ids[0] if collection_ids else "default"
        sparse_hits = self.sparse.search(q, top_k, tenant_id=tenant_id, collection_id=collection_id)
        q_vec = np.array(self.embed_fn([q])[0], dtype=np.float32)
        dense_hits = self.dense.search(q_vec, top_k, tenant_id=tenant_id, collection_id=collection_id)
        merged = merge_candidates(sparse_hits, dense_hits, self.sparse_weight, self.dense_weight)
        sparse_map = dict(sparse_hits)
        dense_map = dict(dense_hits)
        sorted_ids = sorted(merged.keys(), key=lambda x: merged[x], reverse=True)[:top_k]
        candidates: list[RetrievalCandidate] = []
        seen_docs: set[str] = set()
        for cid in sorted_ids:
            ch = self.document_store.get_chunk(cid, tenant_id)
            if not ch:
                continue
            if ch.document_id in seen_docs and len(candidates) > top_k // 2:
                continue
            seen_docs.add(ch.document_id)
            candidates.append(
                RetrievalCandidate(
                    chunk_id=cid,
                    document_id=ch.document_id,
                    text=ch.text,
                    source_uri=ch.source_uri,
                    page_number=ch.page_number,
                    section_title=ch.section_title,
                    sparse_score=sparse_map.get(cid, 0.0),
                    dense_score=dense_map.get(cid, 0.0),
                    hybrid_score=merged[cid],
                    metadata=ch.metadata,
                )
            )
        return candidates
