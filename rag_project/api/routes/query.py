from fastapi import APIRouter, Depends, Request

from rag_project.api.dependencies import get_factory
from rag_project.core.config import get_settings
from rag_project.schemas.api import RAGQueryRequest, RAGQueryResponse
from rag_project.security.auth import verify_api_key
from rag_project.security.rate_limit import RateLimiter

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])
_limiter = RateLimiter()


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: Request,
    body: RAGQueryRequest,
    factory=Depends(get_factory),
) -> RAGQueryResponse:
    settings = get_settings()
    verify_api_key(request, settings)
    rate_key = f"{body.tenant_id}:{request.client.host if request.client else 'unknown'}"
    if not _limiter.allow(rate_key):
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return factory.orchestrator.query(body)
