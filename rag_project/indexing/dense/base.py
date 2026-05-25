from abc import ABC, abstractmethod
import numpy as np


class DenseIndex(ABC):
    @abstractmethod
    def add_vectors(self, chunk_ids: list[str], vectors: np.ndarray, metadata: list[dict] | None = None) -> None: ...

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int, tenant_id: str | None = None, collection_id: str | None = None) -> list[tuple[str, float]]: ...

    @abstractmethod
    def delete_by_chunk_ids(self, chunk_ids: list[str]) -> None: ...

    @abstractmethod
    def persist(self, path: str) -> None: ...

    @abstractmethod
    def load(self, path: str) -> None: ...
