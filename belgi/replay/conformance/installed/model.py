"""Result values for installed conformance execution."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ImplementationCheckResult",
    "InstalledConformanceSuite",
    "NormativeCorpusResult",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class NormativeCorpusResult:
    role: str
    corpus_uri: str
    corpus_sha256: str
    schema_version: str
    source_case_count: int
    executed_case_count: int
    observed_rejection_count: int
    mismatched_case_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.role or not self.corpus_uri or not self.schema_version:
            raise ValueError("Normative conformance identity fields must be non-empty.")
        if len(self.corpus_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.corpus_sha256
        ):
            raise ValueError("Normative corpus SHA-256 must be lowercase hexadecimal.")
        if not (
            0 <= self.executed_case_count <= self.source_case_count
            and 0 <= self.observed_rejection_count <= self.executed_case_count
        ):
            raise ValueError("Normative conformance counts are inconsistent.")
        if len(set(self.mismatched_case_ids)) != len(self.mismatched_case_ids):
            raise ValueError("Normative mismatch identifiers must be unique.")

    @property
    def mismatch_count(self) -> int:
        return len(self.mismatched_case_ids)

    @property
    def successful(self) -> bool:
        return (
            self.executed_case_count == self.source_case_count
            and not self.mismatched_case_ids
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ImplementationCheckResult:
    check_id: str
    classification: str
    scope: str
    corpus_identifier: str
    corpus_version: str
    procedure_identifier: str
    procedure_version: str
    source_case_count: int
    executed_case_count: int
    problem_case_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.classification != "implementation_check":
            raise ValueError(
                "Installed non-normative checks require implementation_check "
                "classification."
            )
        if not (
            self.check_id
            and self.scope
            and self.corpus_identifier
            and self.corpus_version
            and self.procedure_identifier
            and self.procedure_version
        ):
            raise ValueError("Implementation-check identity fields must be non-empty.")
        if not 0 <= self.executed_case_count <= self.source_case_count:
            raise ValueError("Implementation-check counts are inconsistent.")
        if len(set(self.problem_case_ids)) != len(self.problem_case_ids):
            raise ValueError("Implementation-check problem identifiers must be unique.")

    @property
    def problem_count(self) -> int:
        return len(self.problem_case_ids)

    @property
    def successful(self) -> bool:
        return (
            self.executed_case_count == self.source_case_count
            and not self.problem_case_ids
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class InstalledConformanceSuite:
    schema_version: str
    normative_corpora: tuple[NormativeCorpusResult, ...]
    implementation_checks: tuple[ImplementationCheckResult, ...]

    def __post_init__(self) -> None:
        if not self.schema_version:
            raise ValueError("Installed conformance schema version must be non-empty.")
        roles = tuple(result.role for result in self.normative_corpora)
        check_ids = tuple(result.check_id for result in self.implementation_checks)
        if len(set(roles)) != len(roles):
            raise ValueError("Installed normative corpus roles must be unique.")
        if len(set(check_ids)) != len(check_ids):
            raise ValueError(
                "Installed implementation-check identifiers must be unique."
            )

    @property
    def successful(self) -> bool:
        return all(
            result.successful
            for result in (*self.normative_corpora, *self.implementation_checks)
        )
