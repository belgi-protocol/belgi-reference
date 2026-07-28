from __future__ import annotations

from enum import IntEnum

from belgi.carrier import ClaimRecord, EvaluatorCarrier, EvidenceStateCarrier
from belgi.replay.bindings import (
    ConditionEvidenceBindingMatch,
    resolve_evidence_condition_bindings,
)
from belgi.replay.context import (
    EvaluatorParsedT,
    EvaluatorResolvedT,
    EvaluatorT,
    EvidenceParsedT,
    EvidenceResolvedT,
    EvidenceT,
)
from belgi.replay.lifting.model import LiftingTrace
from belgi.replay.report import CACHED_VERDICT_MISMATCH, ReplayWarning

__all__ = ["binding_matches_from_traces", "cached_verdict_warning"]


def cached_verdict_warning(
    *,
    claim_record: ClaimRecord,
    derived_verdict: object,
) -> ReplayWarning | None:
    cached_verdict = claim_record.cached_verdict
    normalized_verdict = _normalize_verdict_value(derived_verdict=derived_verdict)
    if cached_verdict is None or cached_verdict == normalized_verdict:
        return None
    return ReplayWarning(
        type=CACHED_VERDICT_MISMATCH,
        title="Cached verdict does not match the replay-derived verdict.",
        detail=(
            f"The claim record preserves cached verdict {cached_verdict}, but replay "
            f"derived {normalized_verdict}."
        ),
    )


def binding_matches_from_traces(
    *,
    evidence_trace: LiftingTrace[EvidenceParsedT, EvidenceResolvedT, EvidenceT],
    evaluator_trace: LiftingTrace[EvaluatorParsedT, EvaluatorResolvedT, EvaluatorT],
) -> tuple[ConditionEvidenceBindingMatch, ...]:
    if not isinstance(evidence_trace.parsed.value, EvidenceStateCarrier):
        return ()
    if not isinstance(evaluator_trace.parsed.value, EvaluatorCarrier):
        return ()
    return resolve_evidence_condition_bindings(
        evidence_state_carrier=evidence_trace.parsed.value,
        evaluator_carrier=evaluator_trace.parsed.value,
    )


def _normalize_verdict_value(*, derived_verdict: object) -> object:
    if isinstance(derived_verdict, IntEnum):
        return int(derived_verdict)
    if isinstance(derived_verdict, int) and not isinstance(derived_verdict, bool):
        return derived_verdict
    return derived_verdict
