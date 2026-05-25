# RAG Project

Production-minded **Retrieval-Augmented Generation (RAG)** system with hybrid retrieval, hallucination controls, continuous evals, and a versioned API.

## Quick start (local)

```bash
make install
make ingest-sample
make build-index
make run-api
```

Query:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"default","collection_ids":["default"],"query":"What is the refund policy?","top_k":5}'
```

Eval:

```bash
make eval
```

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` for OpenAI generation (otherwise a local grounded stub LLM is used).

## Architecture (v0.2)

New code lives under `rag_project/`:

| Pillar | Modules |
|--------|---------|
| Ingest + dedupe | `ingestion/`, `schemas/documents.py` |
| Hybrid retrieval | `indexing/sparse/bm25_local.py`, `indexing/dense/faiss_ann.py`, `retrieval/hybrid_retriever.py` |
| Reranking + confidence | `retrieval/reranker.py`, `retrieval/source_confidence.py` |
| Hallucination controls | `retrieval/answerability.py`, `generation/constrained_generator.py`, `generation/citation_validator.py`, `generation/claim_verifier.py` |
| API + security | `api/`, `security/` |
| Evals + observability | `evals/`, `observability/` |

See [docs/production_architecture.md](docs/production_architecture.md), [docs/hallucination_controls.md](docs/hallucination_controls.md), [docs/scaling_10m_docs.md](docs/scaling_10m_docs.md).

Legacy paths (`data_ingestion/`, `rag_pipeline/`, `api/main.py`) remain for backward compatibility. `POST /rag` delegates to the new pipeline.

## Core workflow

1. Ingest documents (`POST /api/v1/ingest` or `make ingest-sample`).
2. Build hybrid BM25 + FAISS indexes (`make build-index`).
3. Query with citations (`POST /api/v1/rag/query`).
4. Run golden-set evals (`make eval`).

---

## 2) Repository structure and deep-dive

### Data ingestion (`data_ingestion/`)

- `ingest.py` routes source handling by input type:
  - local directory with PDFs → `connectors/pdf.py`
  - local directory with CSVs → `connectors/csv.py`
  - HTTP source → `connectors/web.py`
  - otherwise treated as API endpoint → `connectors/api.py`
- Writes output docs as `doc_*.txt` in `data/raw`.

**Important implementation notes**
- Connector modules are intentionally lightweight stubs today.
- PDF/web/API connectors emit placeholder text rather than full parsing/fetching logic.
- CSV connector is the most concrete one: it iterates rows and serializes each row into text.

### Data cleaning (`data_cleaning/`)

- `clean.py` reads raw text files, applies basic cleaning, and appends placeholder NER/SRL enrichment.
- `ruleset.yaml` configures cleaning behaviors.
- `ner_srl.py` currently appends static tags (`#NER:[] #SRL:[]`) rather than running an NLP pipeline.

**Current behavior**
- Control-character filtering is implemented.
- HTML stripping, language detection, deduplication and richer normalization are TODOs.

### Embedding service (`embedding_service/`)

- `embed.py`:
  - loads all cleaned `.txt` docs,
  - embeds with SentenceTransformers (`all-MiniLM-L6-v2` by default),
  - builds FAISS `IndexFlatL2`,
  - writes `vector_store/faiss.index` + `vector_store/manifest.json`,
  - writes `data/doc_store.json` mapping numeric IDs to text.

**Operational behavior**
- If no cleaned docs exist, it exits gracefully.
- If FAISS is unavailable, it raises a runtime error.

### Vector store adapters (`vector_store/`)

- `faiss_index.py`: implemented wrapper with `search`.
- `chroma_index.py`: placeholder (`NotImplementedError`).
- `pinecone_index.py`: placeholder (`NotImplementedError`).

### RAG pipeline (`rag_pipeline/`)

- `retrieve.py`:
  - embeds query with SentenceTransformers,
  - loads FAISS index + doc store,
  - returns top-k results with `{doc_id, score, text, meta}`.
  - fallback path: if index missing, returns dummy contexts.
- `rerank.py`: simple ascending score sort (recency logic not yet implemented).
- `generate.py`:
  - if `OPENAI_API_KEY` + `openai` available, calls Chat Completions (`gpt-3.5-turbo`) with concatenated context prompt,
  - otherwise returns deterministic fallback answer.
- `cache.py`: placeholder `lru_cache` helper.

### API service (`api/`)

- FastAPI app with CORS currently open to all origins/methods/headers.
- `POST /rag` accepts `{query, top_k, use_rerank}` and returns typed response:
  - query,
  - retrieved contexts,
  - synthesized answer,
  - confidence score,
  - citations.

### Evaluation (`evaluation/`)

- `metrics.py` implements:
  - `precision_at_k`
  - `mean_reciprocal_rank`
- `evaluate.py` consumes JSONL outputs and writes an aggregate JSON report.

**Caveat**
- Relevance labels are currently mocked (`[1] * len(retrieved_contexts)`), so metrics are structural sanity checks rather than realistic quality measurements.

### Training (`training/`)

- `synthesize_qca.py`: builds QCA triples from prior RAG results (stub-grade synthesis).
- `finetune_lora.py`: fine-tuning scaffold; writes placeholder adapter artifact.

### Frontend (`frontend/`)

- React + TypeScript UI for query submission and result rendering.
- Sends requests to `http://localhost:8000/rag`.
- Displays answer, confidence, citations, and retrieved contexts.

### Utilities & docs

- `scripts/make_dataset.sh`, `scripts/rebuild_index.sh`, `scripts/run_eval.sh` for common flows.
- `docs/architecture.md` provides architecture narrative.
- `docs/eval_report_template.md` provides report template.

---

## 3) End-to-end runbook (local)

## Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)

## Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional if using OpenAI generation:

```bash
export OPENAI_API_KEY=your_key_here
```

## Prepare data + index

```bash
python data_ingestion/ingest.py --source /path/to/input --output data/raw
python data_cleaning/clean.py --input data/raw --output data/clean --rules data_cleaning/ruleset.yaml
python embedding_service/embed.py
```

## Run API

```bash
uvicorn api.main:app --reload
```

Test query:

```bash
curl -X POST http://127.0.0.1:8000/rag \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is this project?","top_k":3,"use_rerank":true}'
```

## Frontend (optional)

```bash
cd frontend
npm install
npm run dev
```

---

## 4) Engineering assessment (comprehensive review)

## Strengths

- Clear modular decomposition by lifecycle stage.
- Runnable baseline with graceful fallbacks when index/API dependencies are absent.
- Typed API contracts and a simple integration test.
- Includes evaluation and training hooks, making future expansion straightforward.

## Gaps / risks

1. **Production readiness:** many connectors and training/eval flows are placeholders.
2. **Model API modernity:** generator uses older `gpt-3.5-turbo`; consider modern model/config abstraction.
3. **Retriever quality controls:** no hybrid retrieval, chunk metadata strategy, or robust scoring normalization.
4. **Reranker simplicity:** no semantic reranker model yet.
5. **Evaluation realism:** no human/ground-truth judgments in current metric pipeline.
6. **Security hardening:** permissive CORS, no auth/rate-limits.
7. **Observability:** no structured tracing/metrics/log correlation.
8. **Data contracts:** some schemas are flexible dicts where stricter typed objects could help.

## Suggested implementation roadmap

### Phase 1: Reliability
- Replace connector stubs with real PDF parsing, HTTP fetch/extract, and API pagination/retries.
- Add deterministic chunking and metadata-rich document model.
- Add structured logging + error handling standards.

### Phase 2: Retrieval quality
- Add BM25 + dense hybrid retrieval.
- Add cross-encoder reranking.
- Introduce query rewriting and citation grounding checks.

### Phase 3: Evaluation + operations
- Add gold datasets and judged relevance labels.
- Add latency/cost dashboards and regression checks in CI.
- Add API auth, request limits, and deployment profiles.

---

## 5) Testing

Run backend tests:

```bash
pytest -q
```

Run evaluation script:

```bash
bash scripts/run_eval.sh
```

---

## 6) Dependencies

Primary dependencies are listed in `requirements.txt` and `pyproject.toml`:

- FastAPI + Uvicorn
- SentenceTransformers
- FAISS
- OpenAI SDK
- Optional vector backends: Chroma, Pinecone
- Dev tooling: pytest, ruff, black

---

## 7) Current maturity summary

This repository is an **excellent architectural starter kit** for RAG systems. It is best treated as a **development scaffold** rather than a finished production system. If you want, the next step can be turning one vertical slice (e.g., PDF→clean→index→query) into fully productionized code with tests and benchmarks.
