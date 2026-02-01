# Evaluation Report

This report summarises the results of evaluating the RAG system.  Fill in each section with the metrics computed by `evaluation/evaluate.py`.

## Summary

Provide a high‑level overview of how the system performed against the evaluation criteria.  Specify whether the system meets the hard thresholds for hallucination rate, context relevance, and precision at top‑k.

## Metrics

| Metric               | Value | Threshold | Pass/Fail |
|----------------------|-------|-----------|-----------|
| Hallucination Rate   |       | ≤ 3%      |           |
| Context Relevance    |       | ≥ 0.8     |           |
| Precision@5          |       | ≥ 0.65    |           |
| Mean Reciprocal Rank |       |           |           |
| Latency (ms)         |       |           |           |
| Cost (USD)           |       |           |           |

## Charts

Include any plots or charts that illustrate the distribution of scores, error analysis, or performance across different query categories.

## Recommendations

If the system fails to meet any threshold, describe potential remediation steps such as data cleaning improvements, better embeddings, hyperparameter tuning, or model selection.