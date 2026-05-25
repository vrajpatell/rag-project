"""Application configuration via Pydantic Settings."""

from __future__ import annotations

import logging
import warnings
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

AppEnv = Literal["local", "dev", "staging", "prod"]
EmbeddingProviderType = Literal["sentence_transformers", "openai"]
SparseBackend = Literal["local_bm25", "opensearch"]
DenseBackend = Literal["faiss", "qdrant", "milvus", "pinecone"]
MetadataStoreType = Literal["sqlite", "postgres"]
ObjectStoreType = Literal["local", "s3", "gcs"]
CacheBackend = Literal["memory", "redis"]
AuthMode = Literal["none", "api_key", "jwt"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnv = "local"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    rag_default_top_k: int = 20
    rag_rerank_top_k: int = 8
    rag_retrieval_candidates: int = 100
    rag_min_source_confidence: float = 0.65
    rag_min_answerability_score: float = 0.70
    rag_require_citations: bool = True
    rag_enable_abstention: bool = True
    rag_sparse_weight: float = 0.45
    rag_dense_weight: float = 0.55

    chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 120
    min_chunk_tokens: int = 20

    embedding_provider: EmbeddingProviderType = "sentence_transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 128

    sparse_index_backend: SparseBackend = "local_bm25"
    dense_index_backend: DenseBackend = "faiss"
    vector_dim: int = 384
    faiss_index_path: str = "./data/indexes/faiss.index"
    faiss_index_type: Literal["flat", "hnsw", "ivf"] = "flat"
    bm25_index_path: str = "./data/indexes/bm25"
    index_manifest_path: str = "./data/indexes/manifest.json"

    metadata_store: MetadataStoreType = "sqlite"
    sqlite_path: str = "./data/metadata.db"
    postgres_dsn: str = ""

    object_store: ObjectStoreType = "local"
    local_object_store_path: str = "./data/objects"

    cache_backend: CacheBackend = "memory"
    redis_url: str = ""
    cache_ttl_seconds: int = 3600

    auth_mode: AuthMode = "none"
    api_keys: str = ""
    jwt_public_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    rate_limit_per_minute: int = 60
    max_request_body_bytes: int = 1_048_576

    otel_enabled: bool = True
    otel_service_name: str = "rag-project"
    prometheus_enabled: bool = True
    log_raw_queries: bool = False

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    data_dir: str = "./data"

    @field_validator("api_keys", mode="before")
    @classmethod
    def strip_api_keys(cls, v: object) -> str:
        return str(v or "").strip()

    def get_api_key_set(self) -> set[str]:
        if not self.api_keys:
            return set()
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    def get_cors_origins_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def validate_production(self) -> list[str]:
        issues: list[str] = []
        if self.app_env == "prod":
            if self.auth_mode == "none":
                issues.append("AUTH_MODE=none is insecure in production")
            if "*" in self.cors_origins:
                issues.append("Wildcard CORS is insecure in production")
            if self.log_raw_queries:
                issues.append("LOG_RAW_QUERIES=true may leak sensitive queries")
        return issues

    def warn_insecure_defaults(self) -> None:
        for msg in self.validate_production():
            warnings.warn(msg, stacklevel=2)
            logger.warning("Production config warning: %s", msg)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.warn_insecure_defaults()
    return settings
