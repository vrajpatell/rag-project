"""Document store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from rag_project.schemas.chunks import Chunk
from rag_project.schemas.documents import NormalizedDocument, RawDocument


class DocumentStore(ABC):
    @abstractmethod
    def save_raw_document(self, doc: RawDocument) -> None: ...

    @abstractmethod
    def save_normalized_document(self, doc: NormalizedDocument) -> None: ...

    @abstractmethod
    def get_document(self, document_id: str, tenant_id: str) -> NormalizedDocument | None: ...

    @abstractmethod
    def get_document_by_hash(
        self, content_hash: str, tenant_id: str, collection_id: str
    ) -> NormalizedDocument | None: ...

    @abstractmethod
    def list_documents(self, tenant_id: str, collection_id: str) -> list[NormalizedDocument]: ...

    @abstractmethod
    def save_chunks(self, chunks: Sequence[Chunk]) -> None: ...

    @abstractmethod
    def get_chunk(self, chunk_id: str, tenant_id: str) -> Chunk | None: ...

    @abstractmethod
    def get_chunks_by_document(self, document_id: str, tenant_id: str) -> list[Chunk]: ...

    @abstractmethod
    def get_chunks_by_ids(self, chunk_ids: list[str], tenant_id: str) -> list[Chunk]: ...
