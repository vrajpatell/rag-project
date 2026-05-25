# Scaling to 10M Documents

## Sharding

- Partition by `tenant_id` + `collection_id`
- Separate BM25 indices per shard; federated search or routing layer
- Vector collections per shard in Qdrant/Milvus/Pinecone

## Indexing

- **Batch embedding** workers with horizontal scale
- **Incremental indexing** for deltas; periodic rebuild for drift
- FAISS: use **IVF + PQ** or **HNSW** at scale; avoid Flat for 10M+
- BM25: OpenSearch/Elasticsearch inverted indexes

## Storage estimates (rough)

- 10M docs × 5 chunks × 500 tokens ≈ 25B tokens (pre-filter)
- Embeddings 384-d float32: ~5 chunks × 10M × 1.5KB ≈ 75GB vectors
- Metadata DB: billions of rows → Postgres with partitioning

## Latency tradeoffs

- Two-stage retrieval: cheap hybrid top-100 → cross-encoder top-8
- Cache hot queries per tenant
- ANN parameters: recall vs latency (efSearch, nprobe)
