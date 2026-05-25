"""Local JSON-backed document store for dev."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from rag_project.schemas.chunks import Chunk
from rag_project.schemas.documents import NormalizedDocument, RawDocument
from rag_project.storage.document_store import DocumentStore


class LocalDocumentStore(DocumentStore):
    def __init__(self, base_path: str = "./data/store") -> None:
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)
        self.docs_path = self.base / "documents.json"
        self.chunks_path = self.base / "chunks.json"
        self.hash_index_path = self.base / "hash_index.json"
        self._load()

    def _load(self) -> None:
        self.documents: dict[str, dict] = {}
        self.chunks: dict[str, dict] = {}
        self.hash_index: dict[str, str] = {}
        if self.docs_path.exists():
            self.documents = json.loads(self.docs_path.read_text())
        if self.chunks_path.exists():
            self.chunks = json.loads(self.chunks_path.read_text())
        if self.hash_index_path.exists():
            self.hash_index = json.loads(self.hash_index_path.read_text())

    def _persist(self) -> None:
        self.docs_path.write_text(json.dumps(self.documents, default=str))
        self.chunks_path.write_text(json.dumps(self.chunks, default=str))
        self.hash_index_path.write_text(json.dumps(self.hash_index))

    def _doc_key(self, tenant_id: str, doc_id: str) -> str:
        return f"{tenant_id}:{doc_id}"

    def save_raw_document(self, doc: RawDocument) -> None:
        pass  # optional persistence for raw

    def save_normalized_document(self, doc: NormalizedDocument) -> None:
        key = self._doc_key(doc.tenant_id, doc.document_id)
        self.documents[key] = doc.model_dump(mode="json")
        hkey = f"{doc.tenant_id}:{doc.collection_id}:{doc.content_hash}"
        self.hash_index[hkey] = doc.document_id
        self._persist()

    def get_document(self, document_id: str, tenant_id: str) -> NormalizedDocument | None:
        data = self.documents.get(self._doc_key(tenant_id, document_id))
        return NormalizedDocument.model_validate(data) if data else None

    def get_document_by_hash(
        self, content_hash: str, tenant_id: str, collection_id: str
    ) -> NormalizedDocument | None:
        doc_id = self.hash_index.get(f"{tenant_id}:{collection_id}:{content_hash}")
        return self.get_document(doc_id, tenant_id) if doc_id else None

    def list_documents(self, tenant_id: str, collection_id: str) -> list[NormalizedDocument]:
        out = []
        for key, data in self.documents.items():
            if key.startswith(f"{tenant_id}:") and data.get("collection_id") == collection_id:
                out.append(NormalizedDocument.model_validate(data))
        return out

    def save_chunks(self, chunks: Sequence[Chunk]) -> None:
        for ch in chunks:
            key = f"{ch.tenant_id}:{ch.chunk_id}"
            self.chunks[key] = ch.model_dump()
        self._persist()

    def get_chunk(self, chunk_id: str, tenant_id: str) -> Chunk | None:
        data = self.chunks.get(f"{tenant_id}:{chunk_id}")
        return Chunk.model_validate(data) if data else None

    def get_chunks_by_document(self, document_id: str, tenant_id: str) -> list[Chunk]:
        return [
            Chunk.model_validate(c)
            for k, c in self.chunks.items()
            if k.startswith(f"{tenant_id}:") and c.get("document_id") == document_id
        ]

    def get_chunks_by_ids(self, chunk_ids: list[str], tenant_id: str) -> list[Chunk]:
        return [c for cid in chunk_ids if (c := self.get_chunk(cid, tenant_id))]
