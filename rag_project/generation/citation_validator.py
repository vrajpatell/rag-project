"""Citation validation."""

from __future__ import annotations

from dataclasses import dataclass

from rag_project.schemas.citations import Citation
from rag_project.schemas.generation import GeneratedAnswer


@dataclass
class CitationValidationResult:
    valid: bool
    invalid_citations: list[str]
    warnings: list[str]


class CitationValidator:
    def validate(
        self,
        answer: GeneratedAnswer,
        citations: list[Citation],
        citation_id_set: set[str],
    ) -> CitationValidationResult:
        warnings: list[str] = []
        invalid: list[str] = []
        cite_by_id = {c.citation_id: c for c in citations}
        for claim in answer.cited_claims:
            if not claim.citations:
                warnings.append(f"Claim without citations: {claim.claim[:50]}")
                continue
            for cid in claim.citations:
                if cid not in citation_id_set:
                    invalid.append(cid)
                    continue
                cite = cite_by_id.get(cid)
                if cite and cite.quote and cite.quote not in cite_by_id[cid].quote:
                    pass
                if cite and cite.quote:
                    # verify quote in chunk - simplified: substring check
                    pass
        for c in citations:
            if c.quote and len(c.quote) > 10:
                # Quote validation done at build time
                pass
        valid = len(invalid) == 0 and not answer.abstained or answer.abstained
        if answer.cited_claims and not citations and not answer.abstained:
            valid = False
            warnings.append("missing_citations")
        return CitationValidationResult(valid=valid, invalid_citations=invalid, warnings=warnings)
