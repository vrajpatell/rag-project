from fastapi import APIRouter, Depends

from rag_project.api.dependencies import get_factory
from rag_project.core.ids import job_id
from rag_project.ingestion.pipeline import IngestionPipeline
from rag_project.schemas.api import IngestRequest, IngestResponse

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(body: IngestRequest, factory=Depends(get_factory)):
    jid = job_id()
    factory.metadata_store.record_ingestion_job(
        jid,
        {
            "job_type": "ingest",
            "tenant_id": body.tenant_id,
            "collection_id": body.collection_id,
            "status": "running",
        },
    )
    pipeline = IngestionPipeline(
        factory.document_store,
        factory.metadata_store,
        chunk_size=factory.settings.chunk_size_tokens,
        chunk_overlap=factory.settings.chunk_overlap_tokens,
    )
    summary, chunks = pipeline.ingest_local(
        body.source_path, body.tenant_id, body.collection_id
    )
    if chunks:
        factory.hybrid_indexer.index_chunks(chunks, mode="incremental")
        factory.hybrid_indexer.persist(
            factory.settings.bm25_index_path,
            factory.settings.faiss_index_path,
        )
    factory.metadata_store.update_ingestion_job_status(
        jid, "succeeded", summary=summary.__dict__
    )
    return IngestResponse(job_id=jid, status="succeeded", summary=summary.__dict__)
