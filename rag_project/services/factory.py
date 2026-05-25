"""Service factory for dependency wiring."""

from __future__ import annotations

from rag_project.cache.memory_cache import MemoryCache
from rag_project.core.config import Settings, get_settings
from rag_project.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from rag_project.generation.constrained_generator import ConstrainedGenerator
from rag_project.indexing.dense.faiss_ann import FaissANNIndex
from rag_project.indexing.hybrid_indexer import HybridIndexer
from rag_project.indexing.sparse.bm25_local import LocalBM25Index
from rag_project.retrieval.hybrid_retriever import HybridRetriever
from rag_project.retrieval.reranker import HeuristicReranker
from rag_project.services.rag_orchestrator import RAGOrchestrator
from rag_project.storage.local_document_store import LocalDocumentStore
from rag_project.storage.sqlite_metadata_store import SQLiteMetadataStore


class ServiceFactory:
    _instance: "ServiceFactory | None" = None

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.document_store = LocalDocumentStore(f"{self.settings.data_dir}/store")
        self.metadata_store = SQLiteMetadataStore(self.settings.sqlite_path)
        self.embedding_provider = SentenceTransformerProvider(self.settings.embedding_model)
        self.sparse_index = LocalBM25Index()
        self.dense_index = FaissANNIndex(
            dim=self.settings.vector_dim,
            index_type=self.settings.faiss_index_type,
        )
        self._load_indexes()
        self.hybrid_indexer = HybridIndexer(
            self.sparse_index,
            self.dense_index,
            lambda texts: self.embedding_provider.embed(texts),
        )
        self.retriever = HybridRetriever(
            self.sparse_index,
            self.dense_index,
            self.document_store,
            lambda texts: self.embedding_provider.embed(texts),
            self.settings.rag_sparse_weight,
            self.settings.rag_dense_weight,
        )
        self.reranker = HeuristicReranker()
        self.generator = ConstrainedGenerator(
            openai_api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
        )
        self.cache = MemoryCache(ttl=self.settings.cache_ttl_seconds)
        self.orchestrator = RAGOrchestrator(
            self.retriever,
            self.reranker,
            self.generator,
            self.settings,
            cache=self.cache,
        )

    def _load_indexes(self) -> None:
        try:
            self.sparse_index.load(self.settings.bm25_index_path)
            self.dense_index.load(self.settings.faiss_index_path)
        except Exception:
            pass

    @classmethod
    def get(cls) -> "ServiceFactory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
