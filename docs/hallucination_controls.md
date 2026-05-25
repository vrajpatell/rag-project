# Hallucination Controls

True **zero hallucination** is not mathematically guaranteed for generative models. This system targets **near-zero** hallucination via layered controls:

1. **Retrieval grounding** — answers must use retrieved chunks only.
2. **Source confidence** — low-confidence evidence triggers warnings or abstention.
3. **Answerability** — insufficient coverage blocks generation.
4. **Constrained prompts** — JSON output, citation IDs, injection defense.
5. **Citation validation** — quotes and IDs checked against chunks.
6. **Claim verification** — lexical overlap between claims and sources.
7. **Abstention fallback** — safe message when guardrails fail.
8. **Continuous eval** — regression gates on faithfulness and abstention precision.

## Abstention example

When evidence is weak, the API returns:

```json
{
  "answer": "I don't have enough reliable information...",
  "abstained": true,
  "confidence_score": 0.0
}
```
