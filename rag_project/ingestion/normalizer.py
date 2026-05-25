"""Text normalization."""

from __future__ import annotations

import re
import unicodedata

from rag_project.core.hashing import SimHash, content_hash


_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_HTML_TAGS = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str, strip_html: bool = True) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _CONTROL_CHARS.sub("", text)
    if strip_html:
        text = _HTML_TAGS.sub(" ", text)
    text = _WHITESPACE.sub(" ", text)
    return text.strip()


def detect_language_placeholder(text: str) -> str:
    """Placeholder language detection; returns 'unknown' or simple heuristic."""
    if not text:
        return "unknown"
    ascii_ratio = sum(1 for c in text if ord(c) < 128) / max(len(text), 1)
    return "en" if ascii_ratio > 0.9 else "unknown"


def build_normalized_fields(
    text: str,
    title: str = "",
    source_uri: str = "",
) -> dict:
    normalized = normalize_text(text)
    return {
        "normalized_text": normalized,
        "content_hash": content_hash(normalized),
        "simhash": SimHash().fingerprint(normalized),
        "title": title or source_uri.split("/")[-1],
        "source_uri": source_uri,
        "language": detect_language_placeholder(normalized),
    }
