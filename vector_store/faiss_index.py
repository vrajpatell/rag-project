from pathlib import Path
import numpy as np

try:
    import faiss  # type: ignore
except ImportError:
    faiss = None


class FaissIndex:
    """Simple wrapper around a FAISS index."""

    def __init__(self, index_path: Path | str) -> None:
        if faiss is None:
            raise RuntimeError("faiss is not available")
        if isinstance(index_path, str):
            index_path = Path(index_path)
        self.index = faiss.read_index(str(index_path))  # type: ignore

    def search(
        self, query_vectors: np.ndarray, top_k: int = 8
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return distances and indices of top_k nearest neighbours."""
        return self.index.search(query_vectors, top_k)  # type: ignore
