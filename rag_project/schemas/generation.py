"""Generation schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CitedClaim(BaseModel):
    claim: str
    citations: list[str] = Field(default_factory=list)


class GeneratedAnswer(BaseModel):
    answer: str
    cited_claims: list[CitedClaim] = Field(default_factory=list)
    confidence_score: float = 0.0
    limitations: list[str] = Field(default_factory=list)
    abstained: bool = False
    abstention_reason: str | None = None
