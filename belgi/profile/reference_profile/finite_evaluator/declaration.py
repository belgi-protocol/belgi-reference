"""Closed trust and decisive-binding grammar for the finite evaluator."""

from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.identifiers.authority import (
    AUTHORITATIVE,
    NON_AUTHORITATIVE,
)
from belgi.profile.reference_profile.identifiers.binding_kinds import SATISFIES
from belgi.profile.reference_profile.identifiers.boundary import EXCLUDED, INCLUDED
from belgi.profile.reference_profile.identifiers.parameters import (
    AUTHORITY_LEVEL_PARAMETER,
    BOUNDARY_PARTICIPATION_PARAMETER,
)

from .constants import (
    FINITE_CONDITIONS,
    RECOGNIZED_BINDING_KINDS,
    RECOGNIZED_SOURCE_CLASSES,
)
from .exceptions import FiniteEvaluatorLiftError
from .model import FiniteEvaluatorDeclaration, FiniteTrustEntry


def finite_evaluator_declaration(
    *, trust_boundaries: object, evidence_condition_bindings: object
) -> FiniteEvaluatorDeclaration:
    """Induce the closed trust map and common decisive reference."""

    return FiniteEvaluatorDeclaration(
        decisive_evidence_identifier=_decisive_evidence_identifier(
            evidence_condition_bindings
        ),
        trust_entries=_trust_entries(trust_boundaries),
    )


def _trust_entries(value: object) -> tuple[FiniteTrustEntry, ...]:
    if not isinstance(value, Mapping):
        raise FiniteEvaluatorLiftError("finite trustBoundaries must be an object.")
    entries: list[FiniteTrustEntry] = []
    for source_class, raw_entry in sorted(value.items()):
        if (
            not isinstance(source_class, str)
            or source_class not in RECOGNIZED_SOURCE_CLASSES
        ):
            raise FiniteEvaluatorLiftError(
                "finite trust boundary key has no exact source-class owner."
            )
        if not isinstance(raw_entry, Mapping) or set(raw_entry) != {"parameters"}:
            raise FiniteEvaluatorLiftError(
                f"finite trust entry {source_class!r} must be closed."
            )
        entries.append(
            _trust_entry(
                source_class=source_class,
                parameters=raw_entry.get("parameters"),
            )
        )
    return tuple(entries)


def _trust_entry(*, source_class: str, parameters: object) -> FiniteTrustEntry:
    if not isinstance(parameters, list) or not parameters:
        raise FiniteEvaluatorLiftError(
            f"finite trust entry {source_class!r} requires ordered parameters."
        )
    first = _finite_declaration_parameter(
        parameters[0], label=f"trust entry {source_class!r}[0]"
    )
    if first[0] != BOUNDARY_PARTICIPATION_PARAMETER:
        raise FiniteEvaluatorLiftError(
            f"finite trust entry {source_class!r} must declare boundary first."
        )
    participation = first[1]
    if participation == EXCLUDED:
        if len(parameters) != 1:
            raise FiniteEvaluatorLiftError(
                f"excluded trust entry {source_class!r} cannot declare authority."
            )
        return FiniteTrustEntry(
            source_class=source_class,
            boundary_participation=participation,
            authority_level=None,
        )
    if participation != INCLUDED or len(parameters) != 2:
        raise FiniteEvaluatorLiftError(
            f"included trust entry {source_class!r} requires one authority."
        )
    second = _finite_declaration_parameter(
        parameters[1], label=f"trust entry {source_class!r}[1]"
    )
    if second[0] != AUTHORITY_LEVEL_PARAMETER or second[1] not in {
        AUTHORITATIVE,
        NON_AUTHORITATIVE,
    }:
        raise FiniteEvaluatorLiftError(
            f"finite trust entry {source_class!r} authority is invalid."
        )
    return FiniteTrustEntry(
        source_class=source_class,
        boundary_participation=participation,
        authority_level=second[1],
    )


def _decisive_evidence_identifier(value: object) -> str | None:
    if not isinstance(value, Mapping):
        raise FiniteEvaluatorLiftError(
            "finite evidenceConditionBindings must be an object."
        )
    decisive_by_condition: dict[str, str] = {}
    for condition, raw_bindings in value.items():
        if not isinstance(condition, str) or condition not in FINITE_CONDITIONS:
            raise FiniteEvaluatorLiftError(
                "finite bindings must be grouped under the selected conditions."
            )
        if not isinstance(raw_bindings, list):
            raise FiniteEvaluatorLiftError(
                f"finite bindings for {condition!r} must be an array."
            )
        decisive = tuple(
            target
            for kind, target in (
                _finite_declaration_binding(raw_binding, condition=condition)
                for raw_binding in raw_bindings
            )
            if kind == SATISFIES
        )
        if len(decisive) > 1:
            raise FiniteEvaluatorLiftError(
                f"finite condition {condition!r} has multiple decisive bindings."
            )
        if decisive:
            decisive_by_condition[condition] = decisive[0]
    targets = set(decisive_by_condition.values())
    if len(targets) > 1:
        raise FiniteEvaluatorLiftError(
            "finite decisive bindings designate inconsistent evidence."
        )
    if set(decisive_by_condition) != FINITE_CONDITIONS:
        return None
    return next(iter(targets))


def _finite_declaration_binding(value: object, *, condition: str) -> tuple[str, str]:
    if not isinstance(value, Mapping) or set(value) != {
        "bindingKindIdentifier",
        "evidenceIdentifiers",
        "parameters",
    }:
        raise FiniteEvaluatorLiftError(
            f"finite binding under {condition!r} must be closed."
        )
    kind = value.get("bindingKindIdentifier")
    if not isinstance(kind, str) or kind not in RECOGNIZED_BINDING_KINDS:
        raise FiniteEvaluatorLiftError(
            f"finite binding under {condition!r} has an unknown kind."
        )
    identifiers = value.get("evidenceIdentifiers")
    if not isinstance(identifiers, list) or not identifiers:
        raise FiniteEvaluatorLiftError(
            f"finite binding under {condition!r} requires evidence identifiers."
        )
    if any(not isinstance(item, str) or not item for item in identifiers):
        raise FiniteEvaluatorLiftError(
            f"finite binding under {condition!r} has an invalid target."
        )
    if len(set(identifiers)) != len(identifiers):
        raise FiniteEvaluatorLiftError(
            f"finite binding under {condition!r} repeats an evidence target."
        )
    parameters = value.get("parameters")
    if not isinstance(parameters, list):
        raise FiniteEvaluatorLiftError(
            f"finite binding under {condition!r} parameters must be an array."
        )
    if kind == SATISFIES and (len(identifiers) != 1 or parameters):
        raise FiniteEvaluatorLiftError(
            f"decisive binding under {condition!r} violates finite grammar."
        )
    return kind, identifiers[0]


def _finite_declaration_parameter(value: object, *, label: str) -> tuple[str, str]:
    if not isinstance(value, Mapping) or set(value) != {
        "parameterIdentifier",
        "value",
    }:
        raise FiniteEvaluatorLiftError(f"finite {label} must be a closed parameter.")
    identifier = value.get("parameterIdentifier")
    parameter_value = value.get("value")
    if not isinstance(identifier, str) or not isinstance(parameter_value, str):
        raise FiniteEvaluatorLiftError(f"finite {label} members must be exact strings.")
    return identifier, parameter_value
