# RAG Project

This repository provides a scaffold for building a production‑grade retrieval‑augmented generation (RAG) pipeline with synthetic data generation, fine‑tuning, evaluation and deployment.  It is organised as a series of modular components that can be developed and tested independently before being orchestrated end‑to‑end.

## Quickstart

1. Clone this repository and install dependencies:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. Copy `.env.example` to `.env` and fill in API keys for OpenAI, HuggingFace, and optional Pinecone credentials.

3. Run data ingestion and cleaning:

    ```bash
    python data_ingestion/ingest.py --source /path/to/files
    python data_cleaning/clean.py --input data/raw --output data/clean
    ```

4. Build embeddings and index:

    ```bash
    python embedding_service/embed.py
    ```

5. Launch the API:

    ```bash
    uvicorn api.main:app --reload
    ```

Refer to the `docs/` folder for a more thorough description of the architecture and evaluation criteria.