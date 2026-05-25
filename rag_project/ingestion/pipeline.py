"""Ingestion pipeline orchestration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rag_project.core.hashing import sha256_bytes
from rag_project.core.ids import document_id_from_hash, new_id
from rag_project.core.time import utc_now
from rag_project.ingestion.chunker import chunk_document
from rag_project.ingestion.dedupe import DedupeState
from rag_project.ingestion.normalizer import build_normalized_fields
from rag_project.ingestion.parsers import get_parser
from rag_project.ingestion.connectors.local_connector import LocalConnector
from rag_project.schemas.chunks import Chunk
from rag_project.schemas.documents import DocumentSource, NormalizedDocument, RawDocument

logger = logging.getLogger(__name__)


@dataclass
class IngestionSummary:
    total_input_documents: int = 0
    parsed_documents: int = 0
    duplicate_documents_skipped: int = 0
    near_duplicates_detected: int = 0
    chunks_created: int = 0
    failed_documents: int = 0
    errors: list[str] = field(default_factory=list)


class IngestionPipeline:
    def __init__(
        self,
        document_store,
        metadata_store,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        min_chunk_tokens: int = 20,
    ) -> None:
        self.document_store = document_store
        self.metadata_store = metadata_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_tokens = min_chunk_tokens

    def ingest_local(
        self,
        source_path: str,
        tenant_id: str = "default",
        collection_id: str = "default",
    ) -> tuple[IngestionSummary, list[Chunk]]:
        connector = LocalConnector(source_path)
        source = DocumentSource(
            source_type="local_file",
            uri=source_path,
            tenant_id=tenant_id,
            collection_id=collection_id,
        )
        summary = IngestionSummary()
        all_chunks: list[Chunk] = []
        dedupe = DedupeState()

        for path in connector.iter_files():
            summary.total_input_documents += 1
            try:
                parser = get_parser(path)
                text, meta = parser.parse(path)
                raw = RawDocument(
                    raw_doc_id=new_id("raw_"),
                    source=source,
                    content_text=text,
                    content_type=path.suffix,
                    checksum=sha256_bytes(path.read_bytes()),
                    metadata=meta,
                )
                self.document_store.save_raw_document(raw)

                fields = build_normalized_fields(text, title=path.name, source_uri=str(path))
                existing = self.document_store.get_document_by_hash(
                    fields["content_hash"], tenant_id, collection_id
                )
                if existing:
                    summary.duplicate_documents_skipped += 1
                    self.metadata_store.mark_duplicate(
                        fields["content_hash"], existing.document_id, tenant_id
                    )
                    continue

                doc = NormalizedDocument(
                    document_id=document_id_from_hash(
                        fields["content_hash"], tenant_id, collection_id
                    ),
                    tenant_id=tenant_id,
                    collection_id=collection_id,
                    title=fields["title"],
                    normalized_text=fields["normalized_text"],
                    source_uri=str(path),
                    content_hash=fields["content_hash"],
                    simhash=fields["simhash"],
                    metadata={**meta, "language": fields["language"]},
                    created_at=utc_now(),
                    updated_at=utc_now(),
                )

                dup = dedupe.check(doc)
                if dup.is_exact_duplicate:
                    summary.duplicate_documents_skipped += 1
                    continue
                if dup.is_near_duplicate:
                    summary.near_duplicates_detected += 1
                    if dup.duplicate_of:
                        dedupe.register_near_duplicate(doc.document_id, dup.duplicate_of)

                dedupe.register(doc)
                self.document_store.save_normalized_document(doc)
                self.metadata_store.upsert_document_metadata(doc)
                summary.parsed_documents += 1

                chunks = chunk_document(
                    doc,
                    self.chunk_size,
                    self.chunk_overlap,
                    self.min_chunk_tokens,
                )
                if chunks:
                    self.document_store.save_chunks(chunks)
                    for ch in chunks:
                        self.metadata_store.upsert_chunk_metadata(ch)
                    all_chunks.extend(chunks)
                    summary.chunks_created += len(chunks)
            except Exception as e:
                summary.failed_documents += 1
                summary.errors.append(f"{path}: {e}")
                logger.exception("Failed to ingest %s", path)

        return summary, all_chunks
