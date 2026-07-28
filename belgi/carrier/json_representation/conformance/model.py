from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class JSONRepresentationCorpusReport:
    corpus_uri: str
    corpus_sha256: str
    schema_version: str
    source_case_count: int
    executed_case_count: int
    observed_rejection_count: int
    mismatched_case_ids: tuple[str, ...]

    @property
    def mismatch_count(self) -> int:
        return len(self.mismatched_case_ids)

    @property
    def successful(self) -> bool:
        return (
            self.executed_case_count == self.source_case_count
            and not self.mismatched_case_ids
        )


__all__ = ["JSONRepresentationCorpusReport"]
