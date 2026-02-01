#!/usr/bin/env bash
set -euo pipefail

# Run evaluation on synthetic or real responses
python evaluation/evaluate.py --results artifacts/eval/rag_results.jsonl --report artifacts/eval/report.json