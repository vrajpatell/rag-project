# Production Architecture

## Overview

The RAG system is organized into independent modules under `rag_project/`:

```mermaid
flowchart TB
    subgraph ingest [Ingestion]
        A[Connectors] --> B[Parsers]
        B --> C[Normalizer]
        C --> D[Dedupe]
        D --> E[Chunker]
    end
    subgraph index [Indexing]
        E --> F[Sparse BM25]
        E --> G[Dense ANN]
    end
    subgraph query [Query Path]
        Q[Query] --> H[Hybrid Retrieval]
        H --> I[Reranker]
        I --> J[Source Confidence]
        J --> K[Answerability]
        K --> L[Constrained Generation]
        L --> M[Citation Validation]
        M --> N[Claim Verification]
        N --> O[Response / Abstain]
    end
    F --> H
    G --> H
```

## Near-zero hallucination strategy

We do not guarantee mathematical zero hallucination. Instead:

- Grounded generation with citation IDs
- Answerability gate before generation
- Source confidence thresholds
- Citation and claim verification
- Abstention when evidence is weak

## Local vs production

| Component | Local | Production |
|-----------|-------|------------|
| Metadata | SQLite | Postgres |
| Object store | Filesystem | S3/GCS |
| Sparse index | Local BM25 | OpenSearch |
| Dense index | FAISS Flat/HNSW | Qdrant/Milvus/Pinecone |
| Cache | Memory | Redis |
| Auth | none/api_key | JWT + API keys |

See [scaling_10m_docs.md](./scaling_10m_docs.md) and [hallucination_controls.md](./hallucination_controls.md).
