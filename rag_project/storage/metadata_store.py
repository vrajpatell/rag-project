from abc import ABC, abstractmethod
from typing import Any

from rag_project.schemas.chunks import Chunk
from rag_project.schemas.documents import NormalizedDocument


class MetadataStore(ABC):
    @abstractmethod
    def upsert_document_metadata(self, doc: NormalizedDocument) -> None: ...

    @abstractmethod
    def upsert_chunk_metadata(self, chunk: Chunk) -> None: ...

    @abstractmethod
    def get_source_metadata(self, document_id: str, tenant_id: str) -> dict[str, Any]: ...

    @abstractmethod
    def mark_duplicate(self, content_hash: str, canonical_id: str, tenant_id: str) -> None: ...

    @abstractmethod
    def record_ingestion_job(self, job_id: str, data: dict[str, Any]) -> None: ...

    @abstractmethod
    def update_ingestion_job_status(self, job_id: str, status: str, **kwargs: Any) -> None: ...

    @abstractmethod
    def get_job(self, job_id: str) -> dict[str, Any] | None: ...
