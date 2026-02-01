#!/usr/bin/env bash
set -euo pipefail

# Rebuild embeddings and FAISS index from cleaned data
python embedding_service/embed.py