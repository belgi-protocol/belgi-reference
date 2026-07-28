from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_ADMISSION_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.agent_admission.identifiers import (
    ALL_CONDITIONS as AGENT_ADMISSION_CONDITIONS,
)
from belgi.profile.companions.python.edition import (
    COMPANION_IDENTIFIER as PYTHON_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.python.supported import SUPPORTED_PYTHON_CONDITIONS
from belgi.profile.reference_profile.config.evaluator_dependencies import (
    reference_profile_evaluator_dependency_designators,
)
from belgi.profile.reference_profile.config.model import AdmissionConfig
from belgi.profile.reference_profile.declarations import (
    EnvironmentCompatibilityDeclaration,
    EvidencePresenceDeclaration,
    OutcomePolicyDeclaration,
    ProfileConditionDeclaration,
    RequiredEvidenceBinding,
    ReviewPolicyDeclaration,
    SourceBoundaryAssignment,
)

from .parameters import (
    ALLOWED_SOURCE_CLASSES_PARAMETER,
    AUTHORITY_LEVEL_PARAMETER,
    BOUNDARY_PARTICIPATION_PARAMETER,
    DECLARATION_PARAMETER,
    EVIDENCE_KIND_PARAMETER,
    MINIMUM_AUTHORITY_PARAMETER,
    MINIMUM_COUNT_PARAMETER,
    JsonCompatible,
)
from .payload import reference_profile_declaration_payload

__all__ = [
    "ReferenceProfileCarrierAlignedDeclarationParameter",
    "ReferenceProfileCarrierAlignedDeclaredCondition",
    "ReferenceProfileCarrierAlignedEvaluator",
    "ReferenceProfileCarrierAlignedEvidenceConditionBinding",
    "ReferenceProfileCarrierAlignedTrustBoundary",
    "reference_profile_aligned_evaluator_carrier",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedDeclarationParameter:
    parameter_identifier: str
    value: JsonCompatible


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedDeclaredCondition:
    condition_identifier: str
    parameters: tuple[ReferenceProfileCarrierAlignedDeclarationParameter, ...]
    determining_source_designator: object | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedTrustBoundary:
    boundary_identifier: str
    parameters: tuple[ReferenceProfileCarrierAlignedDeclarationParameter, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedEvidenceConditionBinding:
    binding_kind_identifier: str
    condition_identifier: str
    evidence_identifiers: tuple[str, ...]
    parameters: tuple[ReferenceProfileCarrierAlignedDeclarationParameter, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedEvaluator:
    declared_conditions: tuple[ReferenceProfileCarrierAlignedDeclaredCondition, ...]
    trust_boundaries: tuple[ReferenceProfileCarrierAlignedTrustBoundary, ...]
    exact_edition_designators: tuple[object, ...]
    evidence_condition_bindings: tuple[
        ReferenceProfileCarrierAlignedEvidenceConditionBinding, ...
    ]


def reference_profile_aligned_evaluator_carrier(
    *,
    admission_artifact: AdmissionConfig,
) -> ReferenceProfileCarrierAlignedEvaluator:
    return ReferenceProfileCarrierAlignedEvaluator(
        declared_conditions=tuple(
            _declared_condition_from_declaration(
                declaration=declaration,
                source_designator=_declaration_determining_source_designator(
                    admission_artifact=admission_artifact,
                    declaration=declaration,
                ),
            )
            for declaration in admission_artifact.condition_declarations
        ),
        trust_boundaries=tuple(
            _trust_boundary_from_assignment(assignment=assignment)
            for assignment in admission_artifact.source_boundary_assignments
        ),
        exact_edition_designators=reference_profile_evaluator_dependency_designators(
            condition_declarations=admission_artifact.condition_declarations
        ),
        evidence_condition_bindings=_carrier_evidence_condition_bindings(
            condition_declarations=admission_artifact.condition_declarations
        ),
    )


def _declared_condition_from_declaration(
    *,
    declaration: ProfileConditionDeclaration,
    source_designator: object,
) -> ReferenceProfileCarrierAlignedDeclaredCondition:
    return ReferenceProfileCarrierAlignedDeclaredCondition(
        condition_identifier=str(declaration.condition_id),
        parameters=(
            ReferenceProfileCarrierAlignedDeclarationParameter(
                parameter_identifier=DECLARATION_PARAMETER,
                value=reference_profile_declaration_payload(declaration=declaration),
            ),
        ),
        determining_source_designator=source_designator,
    )


def _declaration_determining_source_designator(
    *,
    admission_artifact: AdmissionConfig,
    declaration: ProfileConditionDeclaration,
) -> object:
    if declaration.condition_id in AGENT_ADMISSION_CONDITIONS:
        for binding in admission_artifact.selected_companions:
            if str(binding.family_identifier) == str(
                AGENT_ADMISSION_COMPANION_IDENTIFIER
            ):
                return binding.immutable_designator
    if declaration.condition_id in SUPPORTED_PYTHON_CONDITIONS:
        for binding in admission_artifact.selected_companions:
            if str(binding.family_identifier) == str(PYTHON_COMPANION_IDENTIFIER):
                return binding.immutable_designator
    return admission_artifact.profile_edition.immutable_designator


def _trust_boundary_from_assignment(
    *,
    assignment: SourceBoundaryAssignment,
) -> ReferenceProfileCarrierAlignedTrustBoundary:
    parameters = [
        ReferenceProfileCarrierAlignedDeclarationParameter(
            parameter_identifier=BOUNDARY_PARTICIPATION_PARAMETER,
            value=str(assignment.boundary_participation),
        )
    ]
    if assignment.authority_level is not None:
        parameters.append(
            ReferenceProfileCarrierAlignedDeclarationParameter(
                parameter_identifier=AUTHORITY_LEVEL_PARAMETER,
                value=str(assignment.authority_level),
            )
        )
    return ReferenceProfileCarrierAlignedTrustBoundary(
        boundary_identifier=str(assignment.source_class),
        parameters=tuple(parameters),
    )


def _carrier_evidence_condition_bindings(
    *,
    condition_declarations: tuple[ProfileConditionDeclaration, ...],
) -> tuple[ReferenceProfileCarrierAlignedEvidenceConditionBinding, ...]:
    bindings: list[ReferenceProfileCarrierAlignedEvidenceConditionBinding] = []
    for declaration in condition_declarations:
        for required_binding in _required_bindings(declaration=declaration):
            if not required_binding.exact_evidence_identifiers:
                continue
            bindings.append(
                ReferenceProfileCarrierAlignedEvidenceConditionBinding(
                    binding_kind_identifier=str(required_binding.binding_kind),
                    condition_identifier=str(declaration.condition_id),
                    evidence_identifiers=required_binding.exact_evidence_identifiers,
                    parameters=(
                        ReferenceProfileCarrierAlignedDeclarationParameter(
                            parameter_identifier=EVIDENCE_KIND_PARAMETER,
                            value=str(required_binding.evidence_kind),
                        ),
                        ReferenceProfileCarrierAlignedDeclarationParameter(
                            parameter_identifier=MINIMUM_COUNT_PARAMETER,
                            value=required_binding.minimum_count,
                        ),
                        ReferenceProfileCarrierAlignedDeclarationParameter(
                            parameter_identifier=MINIMUM_AUTHORITY_PARAMETER,
                            value=str(required_binding.minimum_authority),
                        ),
                        ReferenceProfileCarrierAlignedDeclarationParameter(
                            parameter_identifier=ALLOWED_SOURCE_CLASSES_PARAMETER,
                            value=[
                                str(source_class)
                                for source_class in required_binding.allowed_source_classes
                            ],
                        ),
                    ),
                )
            )
    return tuple(bindings)


def _required_bindings(
    *,
    declaration: ProfileConditionDeclaration,
) -> tuple[RequiredEvidenceBinding, ...]:
    if isinstance(
        declaration,
        (
            EvidencePresenceDeclaration,
            OutcomePolicyDeclaration,
            ReviewPolicyDeclaration,
            EnvironmentCompatibilityDeclaration,
        ),
    ):
        return declaration.required_bindings
    return ()
