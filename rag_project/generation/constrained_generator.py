"""Constrained grounded generation."""

from __future__ import annotations

import json
import logging
import os

from rag_project.generation.local_stub_llm import LocalStubLLM
from rag_project.generation.prompt_builder import SYSTEM_PROMPT, build_user_prompt
from rag_project.schemas.generation import CitedClaim, GeneratedAnswer
from rag_project.schemas.retrieval import RetrievalCandidate

logger = logging.getLogger(__name__)


class ConstrainedGenerator:
    def __init__(self, openai_api_key: str = "", model: str = "gpt-4o-mini", temperature: float = 0.0) -> None:
        self.api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.temperature = temperature
        self.stub = LocalStubLLM()

    def generate(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        citation_map: dict[str, str],
    ) -> GeneratedAnswer:
        if self.api_key:
            try:
                return self._generate_openai(query, candidates, citation_map)
            except Exception as e:
                logger.warning("OpenAI generation failed: %s", e)
        return self.stub.generate_grounded(query, candidates, citation_map)

    def _generate_openai(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        citation_map: dict[str, str],
    ) -> GeneratedAnswer:
        import openai

        client = openai.OpenAI(api_key=self.api_key)
        user_prompt = build_user_prompt(query, candidates, citation_map)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        return GeneratedAnswer(
            answer=data.get("answer", ""),
            cited_claims=[CitedClaim(**cc) for cc in data.get("cited_claims", [])],
            confidence_score=float(data.get("confidence_score", 0.5)),
            limitations=data.get("limitations", []),
            abstained=bool(data.get("abstained", False)),
            abstention_reason=data.get("abstention_reason"),
        )
