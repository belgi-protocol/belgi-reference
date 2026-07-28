"""Exact-source selection and finite evaluator induction."""

from __future__ import annotations

from collections.abc import Mapping

from belgi.core import (
    ConditionId,
    Evaluator,
    ResolvedConditionSemantics,
    SemanticsKey,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    CHANGE_BASIS_RESOLVED,
    REQUIRED_EVIDENCE_PRESENT,
    REVIEW_POLICY_SATISFIED,
)
from belgi.profile.reference_profile.identifiers.replay_policy import RECORD_CHECK

from .constants import (
    CHANGE_BASIS_SEMANTICS,
    FINITE_CONDITIONS,
    PART4_DESIGNATOR,
    REQUIRED_EVIDENCE_SEMANTICS,
    REVIEW_POLICY_SEMANTICS,
)
from .declaration import finite_evaluator_declaration
from .exceptions import FiniteEvaluatorLiftError
from .model import FiniteCondition

_DOCUMENT_FIELDS = frozenset(
    {
        "kind",
        "replayPolicy",
        "declaredConditions",
        "trustBoundaries",
        "governingSpecificationDesignators",
        "exactEditionDesignators",
        "evidenceConditionBindings",
    }
)
_SEMANTICS = {
    CHANGE_BASIS_RESOLVED: CHANGE_BASIS_SEMANTICS,
    REQUIRED_EVIDENCE_PRESENT: REQUIRED_EVIDENCE_SEMANTICS,
    REVIEW_POLICY_SATISFIED: REVIEW_POLICY_SEMANTICS,
}


def induce_finite_evaluator_document(
    *,
    document: Mapping[str, object],
    resolved_source_designators: frozenset[tuple[str, str, str]],
    available_semantics_keys: frozenset[SemanticsKey],
) -> Evaluator:
    """Induce F only for the exact Part 4 finite selection."""

    if set(document) != _DOCUMENT_FIELDS:
        raise FiniteEvaluatorLiftError("finite evaluator carrier must be closed.")
    if document.get("kind") != "evaluator-carrier":
        raise FiniteEvaluatorLiftError("finite evaluator carrier kind is unsupported.")
    if document.get("replayPolicy") != RECORD_CHECK:
        raise FiniteEvaluatorLiftError("finite evaluator replay policy is unsupported.")
    _require_exact_conditions(document.get("declaredConditions"))
    _require_designator_list(
        document.get("governingSpecificationDesignators"),
        label="governingSpecificationDesignators",
    )
    exact_editions = _require_designator_list(
        document.get("exactEditionDesignators"),
        label="exactEditionDesignators",
    )
    exact_key = (
        PART4_DESIGNATOR.uri,
        PART4_DESIGNATOR.digest.algorithm_id,
        PART4_DESIGNATOR.digest.digest_value,
    )
    if exact_key not in exact_editions or exact_key not in resolved_source_designators:
        raise FiniteEvaluatorLiftError(
            "finite evaluator requires the resolved exact Part 4 source."
        )
    if not set(_SEMANTICS.values()).issubset(available_semantics_keys):
        raise FiniteEvaluatorLiftError(
            "finite evaluator exact-source semantics provider is unavailable."
        )
    declaration = finite_evaluator_declaration(
        trust_boundaries=document.get("trustBoundaries"),
        evidence_condition_bindings=document.get("evidenceConditionBindings"),
    )
    return Evaluator(
        declared_conditions=tuple(
            FiniteCondition(
                condition_id=ConditionId(condition_identifier),
                determining_semantics=ResolvedConditionSemantics(
                    semantics_key=semantics_key
                ),
                finite_declaration=declaration,
            )
            for condition_identifier, semantics_key in sorted(_SEMANTICS.items())
        )
    )


def _require_exact_conditions(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != FINITE_CONDITIONS:
        raise FiniteEvaluatorLiftError(
            "finite evaluator requires exactly its three selected conditions."
        )
    for identifier, raw_declaration in value.items():
        if not isinstance(raw_declaration, Mapping) or set(raw_declaration) != {
            "parameters",
            "determiningSourceDesignator",
        }:
            raise FiniteEvaluatorLiftError(
                f"finite condition {identifier!r} must be closed."
            )
        if raw_declaration.get("parameters") != []:
            raise FiniteEvaluatorLiftError(
                f"finite condition {identifier!r} parameters must be empty."
            )
        if _finite_evaluator_designator_key(
            raw_declaration.get("determiningSourceDesignator")
        ) != (
            PART4_DESIGNATOR.uri,
            PART4_DESIGNATOR.digest.algorithm_id,
            PART4_DESIGNATOR.digest.digest_value,
        ):
            raise FiniteEvaluatorLiftError(
                f"finite condition {identifier!r} must select exact Part 4."
            )


def _require_designator_list(
    value: object, *, label: str
) -> frozenset[tuple[str, str, str]]:
    if not isinstance(value, list):
        raise FiniteEvaluatorLiftError(f"finite {label} must be an array.")
    keys = tuple(_finite_evaluator_designator_key(item) for item in value)
    if len(set(keys)) != len(keys):
        raise FiniteEvaluatorLiftError(f"finite {label} contains duplicates.")
    return frozenset(keys)


def _finite_evaluator_designator_key(value: object) -> tuple[str, str, str]:
    if not isinstance(value, Mapping) or set(value) != {"uri", "digest"}:
        raise FiniteEvaluatorLiftError("finite source designator must be closed.")
    digest = value.get("digest")
    if not isinstance(digest, Mapping) or set(digest) != {
        "algorithmId",
        "digestValue",
    }:
        raise FiniteEvaluatorLiftError("finite source digest must be closed.")
    uri = value.get("uri")
    algorithm = digest.get("algorithmId")
    digest_value = digest.get("digestValue")
    if not isinstance(uri, str) or not uri:
        raise FiniteEvaluatorLiftError(
            "finite source designator members must be non-empty strings."
        )
    if not isinstance(algorithm, str) or not algorithm:
        raise FiniteEvaluatorLiftError(
            "finite source designator members must be non-empty strings."
        )
    if not isinstance(digest_value, str) or not digest_value:
        raise FiniteEvaluatorLiftError(
            "finite source designator members must be non-empty strings."
        )
    return uri, algorithm, digest_value
