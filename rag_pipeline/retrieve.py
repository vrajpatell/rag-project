"""Retrieve top‑k relevant chunks from the vector store."""

import json
import logging
import os
from typing import List, Dict, Any
import numpy as np

from sentence_transformers import SentenceTransformer
from vector_store.faiss_index import FaissIndex

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, index_path: str | None = None, doc_store_path: str | None = None, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.embedder = SentenceTransformer(model_name)
        # Default path to FAISS index
        path = index_path or "vector_store/faiss.index"
        self.index = None
        try:
            self.index = FaissIndex(path)
        except Exception as e:
            logger.warning(f"Failed to load FAISS index from {path}: {e}. Retriever will return dummy results.")

        # Load document store
        self.doc_store = {}
        ds_path = doc_store_path or "data/doc_store.json"
        if os.path.exists(ds_path):
            try:
                with open(ds_path, "r") as f:
                    self.doc_store = json.load(f)
            except Exception as e:
                 logger.warning(f"Failed to load doc store from {ds_path}: {e}")
        else:
            logger.warning(f"Doc store not found at {ds_path}. Using empty store.")

    def retrieve(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        if self.index is None:
            # Fallback for when index is missing
            return [
                {
                    "doc_id": i,
                    "score": 0.0,
                    "text": f"Dummy Document {i} (Index not loaded)",
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
            text = self.doc_store.get(str(idx_int)) or self.doc_store.get(idx_int) or f"Document {idx_int}"
            results.append(
                {
                    "doc_id": idx_int,
                    "score": float(distance),
                    "text": text,
                    "meta": {},
                }
            )
        return results
