"""Legacy entrypoint — delegates to production app."""

from rag_project.api.app import app  # noqa: F401

__all__ = ["app"]