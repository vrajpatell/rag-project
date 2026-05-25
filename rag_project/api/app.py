"""Production FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_project.api.routes import evals, health, ingestion, query
from rag_project.core.config import get_settings
from rag_project.core.logging import setup_logging

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title="RAG Project API", version="0.2.0")

origins = settings.get_cors_origins_list() or ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(query.router)
app.include_router(ingestion.router)
app.include_router(evals.router)


# Legacy /rag endpoint
from api.schemas import RAGRequest, RAGResponse as LegacyRAGResponse
from rag_project.schemas.api import RAGQueryRequest


@app.post("/rag", response_model=LegacyRAGResponse)
async def legacy_rag(request: RAGRequest):
    from rag_project.services.factory import ServiceFactory

    factory = ServiceFactory.get()
    v1_req = RAGQueryRequest(
        tenant_id="default",
        collection_ids=["default"],
        query=request.query,
        top_k=request.top_k,
        require_citations=True,
        allow_abstention=True,
        include_debug=False,
    )
    raw_candidates = factory.retriever.retrieve(
        request.query, "default", ["default"], top_k=request.top_k
    )
    result = factory.orchestrator.query(v1_req)
    contexts = [
        {
            "doc_id": i,
            "text": c.text,
            "score": c.hybrid_score,
            "meta": c.metadata,
        }
        for i, c in enumerate(raw_candidates)
    ]
    return LegacyRAGResponse(
        query=request.query,
        retrieved_contexts=contexts,
        synthesized_answer=result.answer,
        confidence_score=result.confidence_score,
        citations=[c.citation_id for c in result.citations],
    )
