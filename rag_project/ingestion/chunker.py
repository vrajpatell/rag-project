"""Token-aware chunking."""

from __future__ import annotations

import re
from typing import Iterator

from rag_project.core.hashing import content_hash
from rag_project.core.ids import chunk_id as make_chunk_id
from rag_project.schemas.chunks import Chunk
from rag_project.schemas.documents import NormalizedDocument


def estimate_tokens(text: str) -> int:
    """Approximate token count (~4 chars per token)."""
    return max(1, len(text) // 4)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_document(
    doc: NormalizedDocument,
    chunk_size: int = 800,
    overlap: int = 120,
    min_tokens: int = 20,
) -> list[Chunk]:
    text = doc.normalized_text
    if not text:
        return []

    sentences = _split_sentences(text)
    chunks: list[Chunk] = []
    buffer: list[str] = []
    buffer_tokens = 0
    chunk_index = 0
    page_number = doc.metadata.get("page_number")

    def flush() -> None:
        nonlocal chunk_index, buffer, buffer_tokens
        if not buffer:
            return
        chunk_text = " ".join(buffer).strip()
        tok = estimate_tokens(chunk_text)
        if tok < min_tokens and chunk_index > 0:
            return
        ch = content_hash(chunk_text)
        cid = make_chunk_id(doc.document_id, chunk_index, ch)
        chunks.append(
            Chunk(
                chunk_id=cid,
                document_id=doc.document_id,
                tenant_id=doc.tenant_id,
                collection_id=doc.collection_id,
                chunk_index=chunk_index,
                text=chunk_text,
                token_count=tok,
                page_number=page_number,
                section_title=doc.metadata.get("section_title"),
                source_uri=doc.source_uri,
                content_hash=ch,
                metadata=dict(doc.metadata),
            )
        )
        chunk_index += 1
        if overlap > 0 and buffer:
            overlap_text = chunk_text[-overlap * 4 :] if len(chunk_text) > overlap * 4 else chunk_text
            buffer = [overlap_text] if overlap_text else []
            buffer_tokens = estimate_tokens(" ".join(buffer))
        else:
            buffer = []
            buffer_tokens = 0

    for sent in sentences:
        st = estimate_tokens(sent)
        if buffer_tokens + st > chunk_size and buffer:
            flush()
        buffer.append(sent)
        buffer_tokens += st
    flush()
    return chunks


def iter_chunks(
    docs: Iterator[NormalizedDocument],
    chunk_size: int = 800,
    overlap: int = 120,
    min_tokens: int = 20,
) -> Iterator[Chunk]:
    for doc in docs:
        yield from chunk_document(doc, chunk_size, overlap, min_tokens)
