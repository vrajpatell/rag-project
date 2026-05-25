"""Postgres metadata store skeleton."""

from rag_project.storage.metadata_store import MetadataStore


class PostgresMetadataStore(MetadataStore):
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def upsert_document_metadata(self, doc):
        raise NotImplementedError("Implement with asyncpg/SQLAlchemy")

    def upsert_chunk_metadata(self, chunk):
        raise NotImplementedError

    def get_source_metadata(self, document_id, tenant_id):
        return {}

    def mark_duplicate(self, content_hash, canonical_id, tenant_id):
        raise NotImplementedError

    def record_ingestion_job(self, job_id, data):
        raise NotImplementedError

    def update_ingestion_job_status(self, job_id, status, **kwargs):
        raise NotImplementedError

    def get_job(self, job_id):
        return None
