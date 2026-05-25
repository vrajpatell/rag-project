"""Application error types."""

from __future__ import annotations


class RAGError(Exception):
    """Base error for RAG operations."""

    def __init__(self, message: str, code: str = "rag_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(RAGError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="not_found")


class ValidationError(RAGError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="validation_error")


class AuthError(RAGError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, code="unauthorized")


class RateLimitError(RAGError):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, code="rate_limit")


class StorageError(RAGError):
    def __init__(self, message: str = "Storage operation failed") -> None:
        super().__init__(message, code="storage_error")
