#!/usr/bin/env python
"""Generate embeddings for cleaned docs and store them in the vector index."""

from pathlib import Path
import json
from typing import List
import numpy as np

try:
    import faiss  # type: ignore
except ImportError:
    faiss = None  # Only import if available

from sentence_transformers import SentenceTransformer


def load_documents(clean_dir: Path) -> List[str]:
    texts: List[str] = []
    # Sort files to ensure deterministic ID assignment
    for f in sorted(clean_dir.glob("*.txt")):
        texts.append(f.read_text())
    return texts


def embed(texts: List[str], model_name: str) -> np.ndarray:
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings


def build_faiss_index(embeddings: np.ndarray, index_path: Path) -> None:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)  # type: ignore
    index.add(embeddings)
    faiss.write_index(index, str(index_path))  # type: ignore


def main(
    clean_dir: Path, manifest_path: Path, model_name: str = "all-MiniLM-L6-v2"
) -> None:
    clean_texts = load_documents(clean_dir)
    if not clean_texts:
        print(f"No documents found in {clean_dir}")
        return

    emb = embed(clean_texts, model_name)
    index_dir = manifest_path.parent
    index_dir.mkdir(parents=True, exist_ok=True)
    faiss_index_path = index_dir / "faiss.index"
    if faiss is None:
        raise RuntimeError("faiss is not installed")
    build_faiss_index(emb, faiss_index_path)

    manifest = {
        "backend": "faiss",
        "location": str(faiss_index_path),
        "doc_count": len(clean_texts),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # Create and save document store for retrieval
    doc_store = {str(i): text for i, text in enumerate(clean_texts)}
    doc_store_path = Path("data/doc_store.json")
    doc_store_path.parent.mkdir(parents=True, exist_ok=True)
    with open(doc_store_path, "w", encoding="utf-8") as f:
        json.dump(doc_store, f, indent=2)
    print(f"Index and doc store created with {len(clean_texts)} documents.")


if __name__ == "__main__":
    clean_dir = Path("data/clean")
    manifest_path = Path("vector_store/manifest.json")
    main(clean_dir, manifest_path)
