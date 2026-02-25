"""Retrieve top‑k relevant chunks from the vector store."""

import json
import logging
import os
from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer
from vector_store.faiss_index import FaissIndex

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(
        self,
        index_path: str | None = None,
        doc_store_path: str | None = None,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.embedder: SentenceTransformer | None = None
        try:
            self.embedder = SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(
                "Failed to initialize embedder model %s: %s. "
                "Retriever will return dummy results.",
                model_name,
                e,
            )

        # Default path to FAISS index
        path = index_path or "vector_store/faiss.index"
        self.index = None
        try:
            self.index = FaissIndex(path)
        except Exception as e:
            logger.warning(
                "Failed to load FAISS index from %s: %s. "
                "Retriever will return dummy results.",
                path,
                e,
            )

        # Load document store
        self.doc_store: dict[str, Any] = {}
        ds_path = doc_store_path or "data/doc_store.json"
        if os.path.exists(ds_path):
            try:
                with open(ds_path, "r", encoding="utf-8") as f:
                    self.doc_store = json.load(f)
            except Exception as e:
                logger.warning("Failed to load doc store from %s: %s", ds_path, e)
        else:
            logger.warning("Doc store not found at %s. Using empty store.", ds_path)

    def retrieve(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        if self.index is None or self.embedder is None:
            # Fallback for when model/index is missing
            return [
                {
                    "doc_id": i,
                    "score": 0.0,
                    "text": f"Dummy Document {i} (Index or embedder not loaded)",
                    "meta": {},
                }
                for i in range(top_k)
            ]

        query_vec = self.embedder.encode([query], convert_to_numpy=True)
        dists, idxs = self.index.search(query_vec, top_k)
        results: List[Dict[str, Any]] = []
        for distance, idx in zip(dists[0], idxs[0]):
            idx_int = int(idx)
            # Lookup text in doc_store. Key might be string or int.
            text = (
                self.doc_store.get(str(idx_int))
                or self.doc_store.get(idx_int)
                or f"Document {idx_int}"
            )
            results.append(
                {
                    "doc_id": idx_int,
                    "score": float(distance),
                    "text": text,
                    "meta": {},
                }
            )
        return results
