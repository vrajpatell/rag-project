#!/usr/bin/env bash
set -euo pipefail

# Assemble dataset from raw or clean documents.
python data_ingestion/ingest.py --source "$1" --output data/raw
python data_cleaning/clean.py --input data/raw --output data/clean
python embedding_service/embed.py