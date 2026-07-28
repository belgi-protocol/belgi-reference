from __future__ import annotations

from belgi.core import Evaluator, EvidenceState
from belgi.profile.edition import EditionKind, ProfileIdentifier
from belgi.profile.reference_profile.admission_artifact import (
    reference_profile_require_matching_admission_config,
)
from belgi.profile.reference_profile.config.model import AdmissionConfig
from belgi.profile.reference_profile.environment import (
    evidence_uses_environment_envelope,
    require_environment_compatibility_condition,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvaluatorCompileError,
)

__all__ = ["ensure_reference_profile_evaluator_gates"]


def ensure_reference_profile_evaluator_gates(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
    evaluator: Evaluator,
    evidence_state: EvidenceState,
) -> None:
    typed_admission_artifact = reference_profile_require_matching_admission_config(
        admission_artifact=admission_artifact,
        profile_identifier=profile_identifier,
        error_type=ReferenceProfileEvaluatorCompileError,
        owner_label="evaluator validation",
    )
    _require_evaluator_declared_conditions_match(
        admission_artifact=typed_admission_artifact,
        evaluator=evaluator,
    )
    _require_declared_dependency_bindings(admission_artifact=typed_admission_artifact)
    _require_declared_source_boundary_assignments(
        admission_artifact=typed_admission_artifact,
        evidence_state=evidence_state,
    )
    try:
        require_environment_compatibility_condition(
            declared_condition_ids=evaluator.declared_condition_ids,
            environment_envelope_present=evidence_uses_environment_envelope(
                evidence=evidence_state
            ),
            surface_label="environment-envelope material",
        )
    except ValueError as exc:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="environment_terms",
            detail=str(exc),
        ) from exc


def _require_evaluator_declared_conditions_match(
    *,
    admission_artifact: AdmissionConfig,
    evaluator: Evaluator,
) -> None:
    declared_condition_ids = frozenset(
        str(declaration.condition_id)
        for declaration in admission_artifact.condition_declarations
    )
    if {
        str(condition_id) for condition_id in evaluator.declared_condition_ids
    } != declared_condition_ids:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="declared_conditions",
            detail=(
                "evaluator declared conditions do not match the declared "
                "AdmissionConfig declaration set."
            ),
        )


def _require_declared_dependency_bindings(
    *,
    admission_artifact: AdmissionConfig,
) -> None:
    profile_edition = admission_artifact.profile_edition
    selected_companions_by_family = {
        str(binding.family_identifier): binding
        for binding in admission_artifact.selected_companions
    }
    try:
        mandatory_companion_binding = (
            admission_artifact.package_integrity_anchor_companion_binding()
        )
    except ValueError as exc:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="selected_companions",
            detail=str(exc),
        ) from exc
    selected_mandatory_companion = selected_companions_by_family.get(
        str(mandatory_companion_binding.family_identifier)
    )
    if selected_mandatory_companion != mandatory_companion_binding:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="selected_companions",
            detail=(
                "evaluator validation requires the package-integrity-anchor "
                "companion binding selected by the AdmissionConfig artifact."
            ),
        )
    for dependency in admission_artifact.required_evaluator_exact_edition_bindings():
        family_identifier = str(dependency.family_identifier)
        if (
            family_identifier == str(profile_edition.family_identifier)
            and dependency != profile_edition
        ):
            raise ReferenceProfileEvaluatorCompileError(
                semantic_slice="replay_relevant_dependencies",
                detail=(
                    "evaluator dependency binding for the active profile family "
                    "must match the active profile exact edition."
                ),
            )
        if dependency.kind is not EditionKind.COMPANION:
            continue
        selected_companion = selected_companions_by_family.get(family_identifier)
        if selected_companion is None:
            continue
        if selected_companion != dependency:
            raise ReferenceProfileEvaluatorCompileError(
                semantic_slice="replay_relevant_dependencies",
                detail=(
                    "evaluator dependency binding does not match the selected "
                    f"companion exact edition for {family_identifier!r}."
                ),
            )


def _require_declared_source_boundary_assignments(
    *,
    admission_artifact: AdmissionConfig,
    evidence_state: EvidenceState,
) -> None:
    assignments_by_source_class = {
        str(assignment.source_class): assignment
        for assignment in admission_artifact.source_boundary_assignments
    }
    for item in evidence_state.items:
        source_class = getattr(item, "source_class", None)
        if source_class is None:
            continue
        assignment = assignments_by_source_class.get(str(source_class))
        if assignment is None:
            raise ReferenceProfileEvaluatorCompileError(
                semantic_slice="source_boundary_assignments",
                detail=(
                    "evidence item source class has no declared source-boundary "
                    f"assignment: {source_class!s}."
                ),
            )
        boundary_participation = getattr(item, "boundary_participation", None)
        if str(assignment.boundary_participation) != str(boundary_participation):
            raise ReferenceProfileEvaluatorCompileError(
                semantic_slice="source_boundary_assignments",
                detail=(
                    "evidence item boundary participation does not match the "
                    f"declared source-boundary assignment for {source_class!s}."
                ),
            )
        expected_authority = (
            None
            if assignment.authority_level is None
            else str(assignment.authority_level)
        )
        observed_authority_level = getattr(item, "authority_level", None)
        observed_authority = (
            None if observed_authority_level is None else str(observed_authority_level)
        )
        if expected_authority != observed_authority:
            raise ReferenceProfileEvaluatorCompileError(
                semantic_slice="source_boundary_assignments",
                detail=(
                    "evidence item authority level does not match the declared "
                    f"source-boundary assignment for {source_class!s}."
                ),
            )
