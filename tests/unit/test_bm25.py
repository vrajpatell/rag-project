from rag_project.indexing.sparse.bm25_local import LocalBM25Index


def test_bm25_search():
    idx = LocalBM25Index()
    idx.add_documents(
        ["c1", "c2"],
        ["refund within thirty days", "widget bluetooth battery"],
        [{"tenant_id": "default", "collection_id": "default"}] * 2,
    )
    hits = idx.search("refund policy", 5, tenant_id="default", collection_id="default")
    assert hits[0][0] == "c1"
