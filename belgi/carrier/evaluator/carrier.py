"""Evaluator carrier construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from belgi.carrier.evidence_state import EvidenceIdentifier
from belgi.carrier.exceptions import EvaluatorCarrierError
from belgi.carrier.integrity import canonical_json_document_bytes
from belgi.carrier.inventory import (
    DeclarationParameter,
    ImmutableDesignator,
    JsonCompatible,
    carrier_schema_designator,
)

__all__ = [
    "EVALUATOR_CARRIER_MEDIA_TYPE",
    "EVALUATOR_CARRIER_SCHEMA_DESIGNATOR",
    "BindingKindIdentifier",
    "ConditionIdentifier",
    "DeclaredCondition",
    "EvaluatorCarrier",
    "EvidenceConditionBindingDeclaration",
    "ReplayPolicyIdentifier",
    "TrustBoundaryDeclaration",
    "TrustBoundaryIdentifier",
]


EVALUATOR_CARRIER_MEDIA_TYPE = "application/vnd.belgi.evaluator-carrier+json"
EVALUATOR_CARRIER_SCHEMA_DESIGNATOR = carrier_schema_designator(
    schema_name="EvaluatorCarrier.schema.json"
)

ConditionIdentifier = NewType("ConditionIdentifier", str)
TrustBoundaryIdentifier = NewType("TrustBoundaryIdentifier", str)
BindingKindIdentifier = NewType("BindingKindIdentifier", str)
ReplayPolicyIdentifier = NewType("ReplayPolicyIdentifier", str)


def _dedupe_designators(
    *,
    designators: tuple[ImmutableDesignator, ...],
) -> tuple[ImmutableDesignator, ...]:
    seen: set[ImmutableDesignator] = set()
    ordered: list[ImmutableDesignator] = []
    for designator in designators:
        if designator in seen:
            continue
        seen.add(designator)
        ordered.append(designator)
    return tuple(ordered)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeclaredCondition:
    """One declared go condition preserved inside an evaluator carrier."""

    condition_identifier: ConditionIdentifier
    parameters: tuple[DeclarationParameter, ...] = ()
    determining_source_designator: ImmutableDesignator | None = None

    def __post_init__(self) -> None:
        if str(self.condition_identifier).strip() == "":
            raise EvaluatorCarrierError("condition_identifier must be non-empty.")

    def to_json_object(
        self, *, include_identifier: bool = False
    ) -> dict[str, JsonCompatible]:
        payload: dict[str, JsonCompatible] = {
            "parameters": [parameter.to_json_object() for parameter in self.parameters],
        }
        if include_identifier:
            payload["conditionIdentifier"] = str(self.condition_identifier)
        if self.determining_source_designator is not None:
            payload["determiningSourceDesignator"] = (
                self.determining_source_designator.to_json_object()
            )
        return payload


@dataclass(frozen=True, slots=True, kw_only=True)
class TrustBoundaryDeclaration:
    """One trust-boundary declaration preserved inside an evaluator carrier."""

    boundary_identifier: TrustBoundaryIdentifier
    parameters: tuple[DeclarationParameter, ...] = ()

    def __post_init__(self) -> None:
        if str(self.boundary_identifier).strip() == "":
            raise EvaluatorCarrierError("boundary_identifier must be non-empty.")

    def to_json_object(
        self, *, include_identifier: bool = False
    ) -> dict[str, JsonCompatible]:
        payload: dict[str, JsonCompatible] = {
            "parameters": [parameter.to_json_object() for parameter in self.parameters],
        }
        if include_identifier:
            payload["boundaryIdentifier"] = str(self.boundary_identifier)
        return payload


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceConditionBindingDeclaration:
    """One evidence-condition binding preserved inside an evaluator carrier."""

    binding_kind_identifier: BindingKindIdentifier
    condition_identifier: ConditionIdentifier
    evidence_identifiers: tuple[EvidenceIdentifier, ...]
    parameters: tuple[DeclarationParameter, ...] = ()

    def __post_init__(self) -> None:
        if str(self.binding_kind_identifier).strip() == "":
            raise EvaluatorCarrierError("binding_kind_identifier must be non-empty.")
        if str(self.condition_identifier).strip() == "":
            raise EvaluatorCarrierError("condition_identifier must be non-empty.")
        if len(self.evidence_identifiers) == 0:
            raise EvaluatorCarrierError(
                "Evidence-condition bindings shall designate at least one evidence identifier."
            )

    def to_json_object(
        self, *, include_condition_identifier: bool = False
    ) -> dict[str, JsonCompatible]:
        payload: dict[str, JsonCompatible] = {
            "bindingKindIdentifier": str(self.binding_kind_identifier),
            "evidenceIdentifiers": [
                str(evidence_identifier)
                for evidence_identifier in self.evidence_identifiers
            ],
            "parameters": [parameter.to_json_object() for parameter in self.parameters],
        }
        if include_condition_identifier:
            payload["conditionIdentifier"] = str(self.condition_identifier)
        return payload


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluatorCarrier:
    """Replay-relevant evaluator carrier preserving one evaluator declaration set."""

    declared_conditions: tuple[DeclaredCondition, ...]
    replay_policy_identifier: ReplayPolicyIdentifier | None = None
    trust_boundaries: tuple[TrustBoundaryDeclaration, ...] = ()
    governing_specification_designators: tuple[ImmutableDesignator, ...] = ()
    exact_edition_designators: tuple[ImmutableDesignator, ...] = ()
    evidence_condition_bindings: tuple[EvidenceConditionBindingDeclaration, ...] = ()

    def __post_init__(self) -> None:
        if (
            self.replay_policy_identifier is not None
            and str(self.replay_policy_identifier).strip() == ""
        ):
            raise EvaluatorCarrierError("replay_policy_identifier must be non-empty.")
        condition_identifiers = {
            condition.condition_identifier for condition in self.declared_conditions
        }
        if len(condition_identifiers) != len(self.declared_conditions):
            raise EvaluatorCarrierError(
                "Condition identifiers shall be unique within one evaluator carrier."
            )
        if len(
            {
                trust_boundary.boundary_identifier
                for trust_boundary in self.trust_boundaries
            }
        ) != len(self.trust_boundaries):
            raise EvaluatorCarrierError(
                "Trust-boundary identifiers shall be unique within one evaluator carrier."
            )
        for binding in self.evidence_condition_bindings:
            if binding.condition_identifier not in condition_identifiers:
                raise EvaluatorCarrierError(
                    f"Evidence-condition binding references unknown condition identifier: {binding.condition_identifier}"
                )
        governing_specification_set = set(self.governing_specification_designators)
        if len(governing_specification_set) != len(
            self.governing_specification_designators
        ):
            raise EvaluatorCarrierError(
                "Governing specification designators shall be unique."
            )
        exact_edition_set = set(self.exact_edition_designators)
        if len(exact_edition_set) != len(self.exact_edition_designators):
            raise EvaluatorCarrierError(
                "Exact-edition dependency designators shall be unique."
            )

    def required_referenced_source_designators(self) -> tuple[ImmutableDesignator, ...]:
        collected: list[ImmutableDesignator] = []
        for declared_condition in self.declared_conditions:
            if declared_condition.determining_source_designator is not None:
                collected.append(declared_condition.determining_source_designator)
        collected.extend(self.governing_specification_designators)
        collected.extend(self.exact_edition_designators)
        return _dedupe_designators(designators=tuple(collected))

    def to_json_object(self) -> dict[str, JsonCompatible]:
        declared_conditions: dict[str, JsonCompatible] = {}
        for declared_condition in self.declared_conditions:
            declared_conditions[str(declared_condition.condition_identifier)] = (
                declared_condition.to_json_object()
            )

        trust_boundaries: dict[str, JsonCompatible] = {}
        for trust_boundary in self.trust_boundaries:
            trust_boundaries[str(trust_boundary.boundary_identifier)] = (
                trust_boundary.to_json_object()
            )

        evidence_condition_bindings: dict[str, list[JsonCompatible]] = {}
        for evidence_condition_binding in self.evidence_condition_bindings:
            condition_identifier = str(evidence_condition_binding.condition_identifier)
            binding_bucket = evidence_condition_bindings.setdefault(
                condition_identifier, []
            )
            binding_bucket.append(evidence_condition_binding.to_json_object())

        evidence_condition_bindings_json: dict[str, JsonCompatible] = {}
        for condition_identifier, binding_bucket in evidence_condition_bindings.items():
            evidence_condition_bindings_json[condition_identifier] = binding_bucket

        payload: dict[str, JsonCompatible] = {
            "kind": "evaluator-carrier",
            "declaredConditions": declared_conditions,
            "trustBoundaries": trust_boundaries,
            "governingSpecificationDesignators": [
                designator.to_json_object()
                for designator in self.governing_specification_designators
            ],
            "exactEditionDesignators": [
                designator.to_json_object()
                for designator in self.exact_edition_designators
            ],
            "evidenceConditionBindings": evidence_condition_bindings_json,
        }
        if self.replay_policy_identifier is not None:
            payload["replayPolicy"] = str(self.replay_policy_identifier)
        return payload

    def to_json_bytes(self) -> bytes:
        return canonical_json_document_bytes(document=self.to_json_object())
