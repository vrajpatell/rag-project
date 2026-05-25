"""Deduplication logic."""

from __future__ import annotations

from dataclasses import dataclass, field

from rag_project.core.hashing import SimHash, simhash_near_duplicate
from rag_project.schemas.documents import NormalizedDocument


@dataclass
class DedupeResult:
    is_exact_duplicate: bool = False
    is_near_duplicate: bool = False
    duplicate_of: str | None = None
    duplicate_group_id: str | None = None


@dataclass
class DedupeState:
    content_hashes: dict[str, str] = field(default_factory=dict)
    simhashes: dict[str, int] = field(default_factory=dict)
    near_duplicate_groups: dict[str, list[str]] = field(default_factory=dict)
    simhash = SimHash()

    def check(self, doc: NormalizedDocument) -> DedupeResult:
        h = doc.content_hash
        if h in self.content_hashes:
            return DedupeResult(
                is_exact_duplicate=True,
                duplicate_of=self.content_hashes[h],
                duplicate_group_id=h,
            )
        for existing_id, existing_sim in self.simhashes.items():
            if simhash_near_duplicate(doc.simhash, existing_sim):
                group = self.near_duplicate_groups.get(existing_id, [existing_id])
                return DedupeResult(
                    is_near_duplicate=True,
                    duplicate_of=existing_id,
                    duplicate_group_id=group[0] if group else existing_id,
                )
        return DedupeResult()

    def register(self, doc: NormalizedDocument) -> None:
        self.content_hashes[doc.content_hash] = doc.document_id
        self.simhashes[doc.document_id] = doc.simhash

    def register_near_duplicate(self, doc_id: str, group_leader: str) -> None:
        self.near_duplicate_groups.setdefault(group_leader, []).append(doc_id)
