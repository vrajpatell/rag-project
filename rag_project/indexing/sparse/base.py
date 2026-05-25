from abc import ABC, abstractmethod
from typing import Any


class SparseIndex(ABC):
    @abstractmethod
    def add_documents(self, chunk_ids: list[str], texts: list[str], metadata: list[dict[str, Any]]) -> None: ...

    @abstractmethod
    def search(self, query: str, top_k: int, tenant_id: str | None = None, collection_id: str | None = None) -> list[tuple[str, float]]: ...

    @abstractmethod
    def delete_by_chunk_ids(self, chunk_ids: list[str]) -> None: ...

    @abstractmethod
    def persist(self, path: str) -> None: ...

    @abstractmethod
    def load(self, path: str) -> None: ...
