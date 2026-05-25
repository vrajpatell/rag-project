import pytest
from fastapi.testclient import TestClient

from rag_project.api.app import app
from rag_project.services.factory import ServiceFactory


@pytest.fixture
def client():
    factory = ServiceFactory.get()
    from rag_project.workers.ingestion_worker import main as ingest_main
    import sys
    # Run ingestion programmatically
    from rag_project.ingestion.pipeline import IngestionPipeline
    pipeline = IngestionPipeline(factory.document_store, factory.metadata_store)
    summary, chunks = pipeline.ingest_local("examples/docs", "default", "default")
    if chunks:
        factory.hybrid_indexer.index_chunks(chunks, mode="rebuild")
        factory.hybrid_indexer.persist(
            factory.settings.bm25_index_path,
            factory.settings.faiss_index_path,
        )
    return TestClient(app)


def test_refund_query(client):
    r = client.post(
        "/api/v1/rag/query",
        json={
            "tenant_id": "default",
            "collection_ids": ["default"],
            "query": "What is the refund policy?",
            "top_k": 5,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "trace_id" in data
    assert data["abstained"] is False or "refund" in data["answer"].lower()


def test_abstain_unrelated(client):
    r = client.post(
        "/api/v1/rag/query",
        json={
            "query": "What is the capital of France?",
            "allow_abstention": True,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["abstained"] is True


def test_duplicate_skipped():
    factory = ServiceFactory.get()
    from rag_project.ingestion.pipeline import IngestionPipeline
    pipeline = IngestionPipeline(factory.document_store, factory.metadata_store)
    summary, _ = pipeline.ingest_local("examples/docs", "default", "default")
    assert summary.duplicate_documents_skipped >= 1


def test_legacy_rag(client):
    r = client.post("/rag", json={"query": "refund policy", "top_k": 3})
    assert r.status_code == 200
    assert "synthesized_answer" in r.json()
