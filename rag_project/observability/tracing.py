"""OpenTelemetry-compatible tracing wrapper."""

from __future__ import annotations

import contextvars
from contextlib import contextmanager
from typing import Any, Iterator

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")


def get_trace_id() -> str:
    return trace_id_var.get() or ""


@contextmanager
def span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[None]:
    # OTEL SDK can be wired here; local dev uses no-op span
    yield
