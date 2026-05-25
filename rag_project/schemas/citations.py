"""Citation schemas."""

from __future__ import annotations

from pydantic import BaseModel


class Citation(BaseModel):
    citation_id: str
    chunk_id: str
    document_id: str
    source_uri: str = ""
    page_number: int | None = None
    section_title: str | None = None
    quote: str = ""
    start_char: int | None = None
    end_char: int | None = None
    confidence: float = 0.0
