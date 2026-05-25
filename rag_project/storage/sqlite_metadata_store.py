"""SQLite metadata store."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from rag_project.schemas.chunks import Chunk
from rag_project.schemas.documents import NormalizedDocument
from rag_project.storage.metadata_store import MetadataStore


class SQLiteMetadataStore(MetadataStore):
    def __init__(self, db_path: str = "./data/metadata.db") -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT,
                tenant_id TEXT,
                collection_id TEXT,
                content_hash TEXT,
                metadata TEXT,
                PRIMARY KEY (tenant_id, document_id)
            );
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT,
                tenant_id TEXT,
                document_id TEXT,
                metadata TEXT,
                PRIMARY KEY (tenant_id, chunk_id)
            );
            CREATE TABLE IF NOT EXISTS duplicates (
                content_hash TEXT,
                canonical_id TEXT,
                tenant_id TEXT,
                PRIMARY KEY (tenant_id, content_hash)
            );
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                data TEXT
            );
            """
        )
        self.conn.commit()

    def upsert_document_metadata(self, doc: NormalizedDocument) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO documents
               (document_id, tenant_id, collection_id, content_hash, metadata)
               VALUES (?,?,?,?,?)""",
            (
                doc.document_id,
                doc.tenant_id,
                doc.collection_id,
                doc.content_hash,
                json.dumps(doc.metadata),
            ),
        )
        self.conn.commit()

    def upsert_chunk_metadata(self, chunk: Chunk) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO chunks
               (chunk_id, tenant_id, document_id, metadata)
               VALUES (?,?,?,?)""",
            (chunk.chunk_id, chunk.tenant_id, chunk.document_id, json.dumps(chunk.metadata)),
        )
        self.conn.commit()

    def get_source_metadata(self, document_id: str, tenant_id: str) -> dict[str, Any]:
        row = self.conn.execute(
            "SELECT metadata FROM documents WHERE document_id=? AND tenant_id=?",
            (document_id, tenant_id),
        ).fetchone()
        return json.loads(row["metadata"]) if row else {}

    def mark_duplicate(self, content_hash: str, canonical_id: str, tenant_id: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO duplicates VALUES (?,?,?)",
            (content_hash, canonical_id, tenant_id),
        )
        self.conn.commit()

    def record_ingestion_job(self, job_id: str, data: dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO jobs VALUES (?,?)",
            (job_id, json.dumps(data)),
        )
        self.conn.commit()

    def update_ingestion_job_status(self, job_id: str, status: str, **kwargs: Any) -> None:
        job = self.get_job(job_id) or {}
        job["status"] = status
        job.update(kwargs)
        self.record_ingestion_job(job_id, job)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT data FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        return json.loads(row["data"]) if row else None
