"""Framework-owned identity witness for repeated semantic recovery."""

from __future__ import annotations

import math
from dataclasses import fields, is_dataclass
from enum import Enum
from functools import cache
from typing import Any

from belgi.core import Evaluator, EvidenceState, JudgedObject
from belgi.replay.lifting.model import LiftingTrace
from belgi.replay.procedure.model import (
    RecoveredLiftingTraces,
    RecoveredSemanticTuple,
)
from belgi.substrate.importing import is_loaded_type_identity

__all__ = ["framework_recovery_values_match", "semantic_results_match"]


class _UnsupportedRecoveryMaterial(ValueError):
    pass


@cache
def _is_installed_framework_type(value_type: type[object]) -> bool:
    module_name = value_type.__module__
    qualname = value_type.__qualname__
    if not module_name.startswith("belgi.") or "<locals>" in qualname:
        return False
    return is_loaded_type_identity(value_type)


def _framework_structural_token(
    value: object,
    *,
    active_ids: set[int],
) -> tuple[object, ...]:
    value_type = type(value)
    if value is None:
        return ("none",)
    if value_type is bool:
        return ("bool", value)
    if value_type is int:
        return ("int", value)
    if value_type is float and isinstance(value, float):
        if not math.isfinite(value):
            raise _UnsupportedRecoveryMaterial("non-finite recovery number")
        return ("float", value.hex())
    if value_type is str:
        return ("str", value)
    if value_type is bytes:
        return ("bytes", value)
    if isinstance(value, Enum):
        enum_type = type(value)
        if not _is_installed_framework_type(enum_type):
            raise _UnsupportedRecoveryMaterial("non-BELGI enum")
        return (
            "enum",
            enum_type.__module__,
            enum_type.__qualname__,
            value.name,
        )

    identity = id(value)
    if identity in active_ids:
        raise _UnsupportedRecoveryMaterial("cyclic recovery material")
    active_ids.add(identity)
    try:
        if value_type is tuple and isinstance(value, tuple):
            return (
                "tuple",
                tuple(
                    _framework_structural_token(item, active_ids=active_ids)
                    for item in value
                ),
            )
        if value_type is list and isinstance(value, list):
            return (
                "list",
                tuple(
                    _framework_structural_token(item, active_ids=active_ids)
                    for item in value
                ),
            )
        if value_type is frozenset and isinstance(value, frozenset):
            items = tuple(
                _framework_structural_token(item, active_ids=active_ids)
                for item in value
            )
            return ("frozenset", tuple(sorted(items, key=repr)))
        if value_type is dict and isinstance(value, dict):
            items = tuple(
                (
                    _framework_structural_token(key, active_ids=active_ids),
                    _framework_structural_token(item, active_ids=active_ids),
                )
                for key, item in value.items()
            )
            return ("dict", tuple(sorted(items, key=lambda pair: repr(pair[0]))))
        if is_dataclass(value) and not isinstance(value, type):
            if not _is_installed_framework_type(value_type):
                raise _UnsupportedRecoveryMaterial("non-BELGI dataclass")
            projected_fields = tuple(
                (
                    field.name,
                    _framework_structural_token(
                        object.__getattribute__(value, field.name),
                        active_ids=active_ids,
                    ),
                )
                for field in fields(value)
                if field.compare
            )
            return (
                "dataclass",
                value_type.__module__,
                value_type.__qualname__,
                projected_fields,
            )
    except _UnsupportedRecoveryMaterial:
        raise
    except Exception as exc:
        raise _UnsupportedRecoveryMaterial("unreadable recovery material") from exc
    finally:
        active_ids.remove(identity)
    raise _UnsupportedRecoveryMaterial(
        f"unsupported recovery material type: {value_type.__module__}.{value_type.__qualname__}"
    )


def framework_recovery_values_match(*, left: object, right: object) -> bool:
    """Compare only closed BELGI-owned structural projections, fail closed."""

    try:
        left_token = _framework_structural_token(left, active_ids=set())
        right_token = _framework_structural_token(right, active_ids=set())
        return left_token == right_token
    except Exception:
        return False


def _trace_recovered_same_material(
    *,
    left: LiftingTrace[Any, Any, Any],
    right: LiftingTrace[Any, Any, Any],
) -> bool:
    return (
        framework_recovery_values_match(
            left=left.parsed.root_reference,
            right=right.parsed.root_reference,
        )
        and framework_recovery_values_match(
            left=left.resolved.root_reference,
            right=right.resolved.root_reference,
        )
        and framework_recovery_values_match(
            left=left.induced.root_reference,
            right=right.induced.root_reference,
        )
        and framework_recovery_values_match(
            left=left.parsed.value,
            right=right.parsed.value,
        )
        and framework_recovery_values_match(
            left=left.resolved.value,
            right=right.resolved.value,
        )
    )


def _core_recovery_material_matches(
    *,
    left_tuple: RecoveredSemanticTuple[Any, Any, Any],
    right_tuple: RecoveredSemanticTuple[Any, Any, Any],
) -> bool:
    """Witness same-invocation material for exact built-in semantic owners.

    This is not extensional evaluator equality over J x E, cross-implementation
    equivalence, or authorization for caller-defined semantic object types.
    """

    if (
        type(left_tuple.judged) is not JudgedObject
        or type(right_tuple.judged) is not JudgedObject
        or type(left_tuple.evidence) is not EvidenceState
        or type(right_tuple.evidence) is not EvidenceState
        or type(left_tuple.evaluator) is not Evaluator
        or type(right_tuple.evaluator) is not Evaluator
    ):
        return False
    return (
        framework_recovery_values_match(
            left=left_tuple.judged,
            right=right_tuple.judged,
        )
        and framework_recovery_values_match(
            left=left_tuple.evidence,
            right=right_tuple.evidence,
        )
        and framework_recovery_values_match(
            left=left_tuple.evaluator.declared_conditions,
            right=right_tuple.evaluator.declared_conditions,
        )
    )


def semantic_results_match(
    *,
    first_traces: RecoveredLiftingTraces[Any, Any, Any, Any, Any, Any, Any, Any, Any],
    repeated_traces: RecoveredLiftingTraces[
        Any, Any, Any, Any, Any, Any, Any, Any, Any
    ],
    first_tuple: RecoveredSemanticTuple[Any, Any, Any],
    repeated_tuple: RecoveredSemanticTuple[Any, Any, Any],
) -> bool:
    return (
        _trace_recovered_same_material(
            left=first_traces.judged,
            right=repeated_traces.judged,
        )
        and _trace_recovered_same_material(
            left=first_traces.evidence,
            right=repeated_traces.evidence,
        )
        and _trace_recovered_same_material(
            left=first_traces.evaluator,
            right=repeated_traces.evaluator,
        )
        and _core_recovery_material_matches(
            left_tuple=first_tuple,
            right_tuple=repeated_tuple,
        )
    )
