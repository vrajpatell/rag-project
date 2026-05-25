#!/usr/bin/env bash
set -euo pipefail
python -m rag_project.workers.indexing_worker --collection-id default --mode incremental
