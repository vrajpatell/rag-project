"""OpenSearch sparse index adapter skeleton."""

from rag_project.indexing.sparse.base import SparseIndex


class OpenSearchAdapter(SparseIndex):
    def add_documents(self, chunk_ids, texts, metadata=None):
        raise NotImplementedError("Configure OpenSearch cluster for production")

    def search(self, query, top_k, tenant_id=None, collection_id=None):
        raise NotImplementedError

    def delete_by_chunk_ids(self, chunk_ids):
        raise NotImplementedError

    def persist(self, path):
        pass

    def load(self, path):
        pass
