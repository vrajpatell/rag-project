"""FastAPI application exposing the RAG pipeline."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
