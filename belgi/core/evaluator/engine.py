from __future__ import annotations

from belgi.core.evidence.state import EvidenceState

from .exceptions import SatExecutionError
from .model import Condition, Evaluator
from .sat.registry import SatRegistry
from .verdict import GO, NO_GO, Verdict

__all__ = ["active_conditions", "apply_evaluator"]


def active_conditions(
    *,
    evaluator: Evaluator,
    judged: object,
    evidence: EvidenceState,
    sat_registry: SatRegistry,
) -> tuple[Condition, ...]:
    del judged, evidence, sat_registry
    return evaluator.declared_conditions


def apply_evaluator(
    *,
    evaluator: Evaluator,
    judged: object,
    evidence: EvidenceState,
    sat_registry: SatRegistry,
) -> Verdict:
    if not evaluator.declared_conditions:
        return NO_GO

    supported_conditions = active_conditions(
        evaluator=evaluator,
        judged=judged,
        evidence=evidence,
        sat_registry=sat_registry,
    )
    if not supported_conditions:
        return NO_GO

    for condition in supported_conditions:
        if not _evaluate_condition(
            condition=condition,
            judged=judged,
            evidence=evidence,
            sat_registry=sat_registry,
        ):
            return NO_GO
    return GO


def _evaluate_condition(
    *,
    condition: Condition,
    judged: object,
    evidence: EvidenceState,
    sat_registry: SatRegistry,
) -> bool:
    sat = sat_registry.resolve(semantics_key=condition.semantics_key)
    if sat is None:
        return False
    try:
        result = sat(
            judged=judged,
            evidence=evidence,
            condition=condition,
        )
    except Exception as exc:
        raise SatExecutionError(
            f"Sat execution failed for condition {condition.condition_id}."
        ) from exc
    if not isinstance(result, bool):
        raise SatExecutionError(
            f"Sat execution for condition {condition.condition_id} must return bool."
        )
    return result
