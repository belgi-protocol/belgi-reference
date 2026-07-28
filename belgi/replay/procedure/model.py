from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from belgi.carrier import ClaimRecord
from belgi.replay.bindings import ConditionEvidenceBindingMatch
from belgi.replay.context import (
    EvaluatorParsedT,
    EvaluatorResolvedT,
    EvaluatorT,
    EvidenceParsedT,
    EvidenceResolvedT,
    EvidenceT,
    JudgedParsedT,
    JudgedResolvedT,
    JudgedT,
    VerdictT,
)
from belgi.replay.lifting.model import LiftingTrace
from belgi.replay.package_representation.model import RepresentationResult
from belgi.replay.report import ReplayReport

__all__ = ["RecoveredSemanticTuple", "ReplayExecution"]


@dataclass(frozen=True, slots=True, kw_only=True)
class RecoveredSemanticTuple(Generic[JudgedT, EvidenceT, EvaluatorT]):
    judged: JudgedT
    evidence: EvidenceT
    evaluator: EvaluatorT


@dataclass(frozen=True, slots=True, kw_only=True)
class RecoveredLiftingTraces(
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
    ]
):
    judged: LiftingTrace[JudgedParsedT, JudgedResolvedT, JudgedT]
    evidence: LiftingTrace[EvidenceParsedT, EvidenceResolvedT, EvidenceT]
    evaluator: LiftingTrace[EvaluatorParsedT, EvaluatorResolvedT, EvaluatorT]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayExecution(
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
    report: ReplayReport[VerdictT]
    representation_result: RepresentationResult | None = None
    claim_record: ClaimRecord | None = None
    semantic_tuple: RecoveredSemanticTuple[JudgedT, EvidenceT, EvaluatorT] | None = None
    judged_trace: LiftingTrace[JudgedParsedT, JudgedResolvedT, JudgedT] | None = None
    evidence_trace: (
        LiftingTrace[EvidenceParsedT, EvidenceResolvedT, EvidenceT] | None
    ) = None
    evaluator_trace: (
        LiftingTrace[EvaluatorParsedT, EvaluatorResolvedT, EvaluatorT] | None
    ) = None
    binding_matches: tuple[ConditionEvidenceBindingMatch, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "binding_matches", tuple(self.binding_matches))
        if self.report.derived_verdict is None and self.semantic_tuple is not None:
            raise ValueError(
                "Failed replay executions must not carry a semantic tuple."
            )
        if self.report.derived_verdict is not None and self.semantic_tuple is None:
            raise ValueError("Successful replay executions require a semantic tuple.")

    @property
    def successful(self) -> bool:
        return self.report.derived_verdict is not None

    @property
    def derived_verdict(self) -> VerdictT | None:
        return self.report.derived_verdict
