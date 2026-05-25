#!/usr/bin/env bash
set -euo pipefail
python -m rag_project.workers.ingestion_worker --source examples/docs --tenant-id default --collection-id default
