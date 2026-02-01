"""FastAPI application exposing the RAG pipeline."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from .schemas import RAGRequest, RAGResponse
from rag_pipeline.retrieve import Retriever
from rag_pipeline.rerank import rerank_by_recency
from rag_pipeline.generate import synthesize_answer


app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

retriever = Retriever()


@app.post("/rag", response_model=RAGResponse)
async def rag_endpoint(request: RAGRequest) -> RAGResponse:
    results = retriever.retrieve(request.query, top_k=request.top_k)
    if request.use_rerank:
        results = rerank_by_recency(results)
    response = synthesize_answer(request.query, results)
    return RAGResponse(**response)

# Serve React App
# Mount the static directory. We'll ensure "frontend/dist" is copied to "app/static" in Docker
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # API routes are already handled above.
        # This catch-all serves index.html for any other route to support client-side routing.
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
             return FileResponse(index_path)
        return {"error": "Frontend not found"}