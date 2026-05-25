"""Safe fallback responses."""

from rag_project.schemas.api import RAGQueryResponse
from rag_project.schemas.citations import Citation
from rag_project.schemas.generation import CitedClaim


ABSTAIN_MESSAGE = (
    "I don't have enough reliable information in the indexed documents to answer this confidently."
)


def build_abstain_response(
    reason: str,
    trace_id: str,
    warnings: list[str] | None = None,
) -> RAGQueryResponse:
    return RAGQueryResponse(
        answer=ABSTAIN_MESSAGE,
        abstained=True,
        abstention_reason=reason,
        confidence_score=0.0,
        citations=[],
        cited_claims=[],
        warnings=warnings or [],
        trace_id=trace_id,
    )


def build_citations_from_candidates(candidates, citation_map: dict[str, str]) -> list[Citation]:
    citations: list[Citation] = []
    for c in candidates:
        cid = citation_map.get(c.chunk_id)
        if not cid:
            continue
        quote = c.text[:200].strip()
        citations.append(
            Citation(
                citation_id=cid,
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                source_uri=c.source_uri,
                page_number=c.page_number,
                section_title=c.section_title,
                quote=quote,
                confidence=min(1.0, (c.rerank_score or c.hybrid_score)),
            )
        )
    return citations
