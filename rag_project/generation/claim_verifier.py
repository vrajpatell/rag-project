"""Claim verification against sources."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rag_project.schemas.generation import GeneratedAnswer
from rag_project.schemas.retrieval import RetrievalCandidate


@dataclass
class ClaimVerificationResult:
    supported: bool
    unsupported_claims: list[str]
    support_ratio: float


class ClaimVerifier:
    def verify(
        self,
        answer: GeneratedAnswer,
        candidates: list[RetrievalCandidate],
        citation_to_chunk: dict[str, str],
    ) -> ClaimVerificationResult:
        chunk_text = {c.chunk_id: c.text.lower() for c in candidates}
        unsupported: list[str] = []
        total = 0
        supported_count = 0
        for claim in answer.cited_claims:
            total += 1
            claim_lower = claim.claim.lower()
            found = False
            for cid in claim.citations:
                chunk_id = citation_to_chunk.get(cid)
                if not chunk_id:
                    continue
                text = chunk_text.get(chunk_id, "")
                tokens = set(re.findall(r"\w+", claim_lower))
                if tokens:
                    overlap = len(tokens & set(re.findall(r"\w+", text))) / len(tokens)
                    if overlap >= 0.3 or claim_lower[:40] in text:
                        found = True
                        break
            if found:
                supported_count += 1
            else:
                unsupported.append(claim.claim)
        ratio = supported_count / total if total else 1.0
        return ClaimVerificationResult(
            supported=ratio >= 0.25,
            unsupported_claims=unsupported,
            support_ratio=ratio,
        )
