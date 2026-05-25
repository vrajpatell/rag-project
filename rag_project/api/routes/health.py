from fastapi import APIRouter
from fastapi.responses import Response

from rag_project.observability.metrics import metrics_response
from rag_project.services.factory import ServiceFactory

router = APIRouter(tags=["health"])


@router.get("/api/v1/health/live")
async def live():
    return {"status": "ok"}


@router.get("/api/v1/health/ready")
async def ready():
    factory = ServiceFactory.get()
    indexed = len(factory.sparse_index.chunk_ids) > 0
    return {"status": "ready" if indexed else "degraded", "indexed_chunks": len(factory.sparse_index.chunk_ids)}


@router.get("/health/live")
async def live_legacy():
    return await live()


@router.get("/health/ready")
async def ready_legacy():
    return await ready()


@router.get("/metrics")
async def metrics():
    body, content_type = metrics_response()
    return Response(content=body, media_type=content_type)
