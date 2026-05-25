#!/usr/bin/env bash
set -euo pipefail
curl -s -X POST http://127.0.0.1:8000/api/v1/rag/query \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"default","collection_ids":["default"],"query":"What is the refund policy?","top_k":5}' | python -m json.tool
