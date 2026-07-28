from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from belgi.carrier import ImmutableDesignator, PackageIntegrityAnchor

if TYPE_CHECKING:
    from .lifting.model import CarrierLiftingAdapter

__all__ = [
    "EvaluatorParsedT",
    "EvaluatorResolvedT",
    "EvaluatorT",
    "EvidenceParsedT",
    "EvidenceResolvedT",
    "EvidenceT",
    "JudgedParsedT",
    "JudgedResolvedT",
    "JudgedT",
    "PackageIntegrityAnchorVerification",
    "PackageIntegrityAnchorVerifier",
    "ReplayContext",
    "VerdictDeriver",
    "VerdictT",
]

JudgedParsedT = TypeVar("JudgedParsedT")
JudgedResolvedT = TypeVar("JudgedResolvedT")
EvidenceParsedT = TypeVar("EvidenceParsedT")
EvidenceResolvedT = TypeVar("EvidenceResolvedT")
EvaluatorParsedT = TypeVar("EvaluatorParsedT")
EvaluatorResolvedT = TypeVar("EvaluatorResolvedT")
JudgedT = TypeVar("JudgedT")
EvidenceT = TypeVar("EvidenceT")
EvaluatorT = TypeVar("EvaluatorT")
VerdictT = TypeVar("VerdictT")
JudgedInputT = TypeVar("JudgedInputT", contravariant=True)
EvidenceInputT = TypeVar("EvidenceInputT", contravariant=True)
EvaluatorInputT = TypeVar("EvaluatorInputT", contravariant=True)
VerdictOutputT = TypeVar("VerdictOutputT", covariant=True)


class VerdictDeriver(
    Protocol[JudgedInputT, EvidenceInputT, EvaluatorInputT, VerdictOutputT]
):
    def __call__(
        self,
        *,
        judged: JudgedInputT,
        evidence: EvidenceInputT,
        evaluator: EvaluatorInputT,
    ) -> VerdictOutputT: ...


class PackageIntegrityAnchorVerifier(Protocol):
    def select(
        self,
        *,
        anchor: PackageIntegrityAnchor,
    ) -> PackageIntegrityAnchorVerification: ...

    def __call__(
        self,
        *,
        anchor: PackageIntegrityAnchor,
        manifest_bytes: bytes,
    ) -> PackageIntegrityAnchorVerification: ...

    def supports_digest_algorithm_identifier(self, *, identifier: str) -> bool: ...

    def supports_digest_algorithm_designator(
        self,
        *,
        designator: ImmutableDesignator,
    ) -> bool: ...


class PackageIntegrityAnchorVerification(Protocol):
    @property
    def accepted(self) -> bool: ...

    @property
    def code(self) -> str: ...

    @property
    def detail(self) -> str: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayContext(
    Generic[
        JudgedParsedT,
        JudgedResolvedT,
        EvidenceParsedT,
        EvidenceResolvedT,
        EvaluatorParsedT,
        EvaluatorResolvedT,
        JudgedT,
        EvidenceT,
        EvaluatorT,
        VerdictT,
    ]
):
    judged_lifting: CarrierLiftingAdapter[JudgedParsedT, JudgedResolvedT, JudgedT]
    evidence_lifting: CarrierLiftingAdapter[
        EvidenceParsedT, EvidenceResolvedT, EvidenceT
    ]
    evaluator_lifting: CarrierLiftingAdapter[
        EvaluatorParsedT, EvaluatorResolvedT, EvaluatorT
    ]
    package_integrity_anchor_verifier: PackageIntegrityAnchorVerifier
    verdict_deriver: VerdictDeriver[JudgedT, EvidenceT, EvaluatorT, VerdictT]
