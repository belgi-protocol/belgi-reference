from __future__ import annotations

from belgi.core import (
    Evaluator,
    EvidenceState,
    JudgedObject,
    SatRegistry,
    Verdict,
    apply_evaluator,
)

from .context import VerdictDeriver

__all__ = [
    "core_verdict_deriver",
]


def core_verdict_deriver(
    *,
    sat_registry: SatRegistry,
) -> VerdictDeriver[JudgedObject, EvidenceState, Evaluator, Verdict]:
    def derive(
        *,
        judged: JudgedObject,
        evidence: EvidenceState,
        evaluator: Evaluator,
    ) -> Verdict:
        return apply_evaluator(
            evaluator=evaluator,
            judged=judged,
            evidence=evidence,
            sat_registry=sat_registry,
        )

    return derive
