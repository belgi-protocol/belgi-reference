from __future__ import annotations

from collections.abc import Container
from dataclasses import dataclass

from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_ADMISSION_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.agent_admission.identifiers import (
    ALL_CONDITIONS as AGENT_ADMISSION_CONDITIONS,
)
from belgi.profile.companions.package_integrity_anchor.edition import (
    require_package_integrity_anchor_companion,
)
from belgi.profile.companions.python.edition import (
    COMPANION_IDENTIFIER as PYTHON_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.python.supported import SUPPORTED_PYTHON_CONDITIONS
from belgi.profile.edition import (
    EditionKind,
    ExactEditionBinding,
    ImmutableDesignator,
    is_controlled_belgi_edition_family_identifier,
)
from belgi.profile.governance import ReplayPolicyId
from belgi.profile.reference_profile.config.evaluator_dependencies import (
    reference_profile_evaluator_dependency_bindings,
    reference_profile_evaluator_dependency_designators,
    validate_reference_profile_evaluator_carrier,
    validate_reference_profile_source_boundary_assignments,
)
from belgi.profile.reference_profile.config.exact_editions import (
    resolve_reference_profile_companion_binding,
)
from belgi.profile.reference_profile.declarations import (
    EnvironmentTermValue,
    ProfileConditionDeclaration,
    SourceBoundaryAssignment,
)
from belgi.profile.reference_profile.environment import (
    require_environment_compatibility_condition,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileAdmissionCompileError,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    ALL_CONDITIONS,
    FOUNDATION_CONDITIONS,
)
from belgi.profile.reference_profile.identifiers.replay_policy import (
    ALL_REPLAY_POLICIES,
)
from belgi.profile.source_material import (
    ProfileExactEditionSource,
    built_in_exact_edition_source,
)

__all__ = [
    "AdmissionConfig",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class AdmissionConfig:
    profile_edition: ExactEditionBinding
    replay_policy: ReplayPolicyId
    condition_declarations: tuple[ProfileConditionDeclaration, ...]
    source_boundary_assignments: tuple[SourceBoundaryAssignment, ...]
    environment_terms: tuple[EnvironmentTermValue, ...]
    selected_companions: tuple[ExactEditionBinding, ...]

    def __post_init__(self) -> None:
        if self.profile_edition.kind is not EditionKind.PROFILE:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="profile_exact_edition",
                detail=(
                    "AdmissionConfig.profile_edition must be a profile "
                    "exact-edition binding."
                ),
            )
        if self.replay_policy not in ALL_REPLAY_POLICIES:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="replay_policy",
                detail=f"unsupported replay policy: {self.replay_policy!r}.",
            )
        if not self.condition_declarations:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="condition_declarations",
                detail="condition_declarations must not be empty.",
            )
        seen_condition_ids: set[str] = set()
        for declaration in self.condition_declarations:
            condition_id = str(declaration.condition_id)
            if condition_id in seen_condition_ids:
                raise ReferenceProfileAdmissionCompileError(
                    semantic_slice="condition_declarations",
                    detail=(
                        "duplicate condition declaration for "
                        f"condition_id {condition_id!r}."
                    ),
                )
            seen_condition_ids.add(condition_id)
        agent_admission_condition_set = set(AGENT_ADMISSION_CONDITIONS)
        python_condition_set = set(SUPPORTED_PYTHON_CONDITIONS)
        known_condition_ids = (
            set(ALL_CONDITIONS) | agent_admission_condition_set | python_condition_set
        )
        unsupported = {
            str(declaration.condition_id)
            for declaration in self.condition_declarations
            if declaration.condition_id not in known_condition_ids
        }
        if unsupported:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="condition_declarations",
                detail=(
                    "AdmissionConfig accepts only reference-profile or selected "
                    "companion condition "
                    "identifiers: " + ", ".join(sorted(unsupported))
                ),
            )
        try:
            require_package_integrity_anchor_companion(
                selected_companions=self.selected_companions
            )
        except ValueError as exc:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="selected_companions",
                detail=str(exc),
            ) from exc
        _admission_config_require_companion_condition_consistency(
            condition_declarations=self.condition_declarations,
            selected_companions=self.selected_companions,
            companion_identifier=str(AGENT_ADMISSION_COMPANION_IDENTIFIER),
            companion_condition_ids=agent_admission_condition_set,
            companion_label="agent-admission",
        )
        _admission_config_require_companion_condition_consistency(
            condition_declarations=self.condition_declarations,
            selected_companions=self.selected_companions,
            companion_identifier=str(PYTHON_COMPANION_IDENTIFIER),
            companion_condition_ids=python_condition_set,
            companion_label="Python condition vocabulary",
        )
        declared_condition_ids = {
            declaration.condition_id for declaration in self.condition_declarations
        }
        required_condition_ids = set(FOUNDATION_CONDITIONS)
        missing_required = required_condition_ids - declared_condition_ids
        if missing_required:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="condition_declarations",
                detail=(
                    "AdmissionConfig requires the foundation profile conditions: "
                    + ", ".join(
                        sorted(str(condition_id) for condition_id in missing_required)
                    )
                ),
            )
        additional_conditions = declared_condition_ids - required_condition_ids
        if not additional_conditions:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="condition_declarations",
                detail=(
                    "AdmissionConfig requires at least one additional go condition "
                    "beyond change-basis-resolved and required-evidence-present."
                ),
            )
        try:
            require_environment_compatibility_condition(
                declared_condition_ids=declared_condition_ids,
                environment_envelope_present=bool(self.environment_terms),
                surface_label="AdmissionConfig.environment_terms",
            )
        except ValueError as exc:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="environment_terms",
                detail=str(exc),
            ) from exc
        for declaration in self.condition_declarations:
            seen_replay_relevant_dependencies: set[ExactEditionBinding] = set()
            for dependency in declaration.replay_relevant_dependencies:
                if dependency in seen_replay_relevant_dependencies:
                    condition_id = str(declaration.condition_id)
                    raise ReferenceProfileAdmissionCompileError(
                        semantic_slice="replay_relevant_dependencies",
                        detail=(
                            "duplicate replay_relevant_dependency binding for "
                            f"{condition_id!r}: "
                            f"{dependency.family_identifier!r}@"
                            f"{dependency.version_designator!r}."
                        ),
                    )
                seen_replay_relevant_dependencies.add(dependency)
                family_identifier = str(dependency.family_identifier)
                if not is_controlled_belgi_edition_family_identifier(
                    value=family_identifier
                ):
                    raise ReferenceProfileAdmissionCompileError(
                        semantic_slice="replay_relevant_dependencies",
                        detail=(
                            "replay_relevant_dependencies accepts BELGI "
                            "exact-edition bindings only; each family identifier "
                            "must use the controlled BELGI HTTPS namespace."
                        ),
                    )
                if dependency.kind not in {
                    EditionKind.COMPANION,
                    EditionKind.EXTERNAL,
                    EditionKind.PROFILE,
                }:
                    raise ReferenceProfileAdmissionCompileError(
                        semantic_slice="replay_relevant_dependencies",
                        detail=(
                            "replay_relevant_dependencies must use companion, "
                            "external, or profile exact-edition bindings."
                        ),
                    )
        try:
            validate_reference_profile_source_boundary_assignments(
                source_boundary_assignments=self.source_boundary_assignments,
                condition_declarations=self.condition_declarations,
            )
        except ValueError as exc:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="source_boundary_assignments",
                detail=str(exc),
            ) from exc

    def declaration_for(self, *, condition_id: str) -> ProfileConditionDeclaration:
        for declaration in self.condition_declarations:
            if str(declaration.condition_id) == condition_id:
                return declaration
        raise KeyError(condition_id)

    def required_evaluator_exact_edition_bindings(
        self,
    ) -> tuple[ExactEditionBinding, ...]:
        return reference_profile_evaluator_dependency_bindings(
            condition_declarations=self.condition_declarations,
        )

    def required_evaluator_exact_edition_designators(
        self,
    ) -> tuple[ImmutableDesignator, ...]:
        return reference_profile_evaluator_dependency_designators(
            condition_declarations=self.condition_declarations,
        )

    def exact_edition_sources(self) -> tuple[ProfileExactEditionSource, ...]:
        bindings = tuple(
            dict.fromkeys(
                (
                    self.profile_edition,
                    *self.selected_companions,
                    *self.required_evaluator_exact_edition_bindings(),
                )
            )
        )
        return tuple(
            built_in_exact_edition_source(binding=binding) for binding in bindings
        )

    def package_integrity_anchor_companion_binding(self) -> ExactEditionBinding:
        return require_package_integrity_anchor_companion(
            selected_companions=self.selected_companions
        )

    def validate_evaluator_carrier(
        self,
        *,
        evaluator_carrier: object,
    ) -> None:
        validate_reference_profile_evaluator_carrier(
            evaluator_carrier=evaluator_carrier,
            condition_declarations=self.condition_declarations,
        )


def _admission_config_companion_binding(
    *,
    selected_companions: tuple[ExactEditionBinding, ...],
    companion_identifier: str,
) -> ExactEditionBinding | None:
    for binding in selected_companions:
        if str(binding.family_identifier) == companion_identifier:
            return binding
    return None


def _admission_config_require_companion_condition_consistency(
    *,
    condition_declarations: tuple[ProfileConditionDeclaration, ...],
    selected_companions: tuple[ExactEditionBinding, ...],
    companion_identifier: str,
    companion_condition_ids: Container[object],
    companion_label: str,
) -> None:
    selected_companion = _admission_config_companion_binding(
        selected_companions=selected_companions,
        companion_identifier=companion_identifier,
    )
    expected_companion = resolve_reference_profile_companion_binding(
        companion_identifier=companion_identifier,
    )
    if selected_companion is not None and selected_companion != expected_companion:
        raise ReferenceProfileAdmissionCompileError(
            semantic_slice="selected_companions",
            detail=(
                f"selected {companion_label} companion binding must match the "
                "supported reference-profile exact edition."
            ),
        )
    companion_declarations = tuple(
        declaration
        for declaration in condition_declarations
        if declaration.condition_id in companion_condition_ids
    )
    if companion_declarations and selected_companion is None:
        raise ReferenceProfileAdmissionCompileError(
            semantic_slice="selected_companions",
            detail=(
                f"{companion_label} condition declarations require the "
                f"{companion_label} companion exact edition."
            ),
        )
    for declaration in companion_declarations:
        if selected_companion not in declaration.replay_relevant_dependencies:
            raise ReferenceProfileAdmissionCompileError(
                semantic_slice="replay_relevant_dependencies",
                detail=(
                    f"{companion_label} condition declarations must preserve the "
                    f"selected {companion_label} companion exact edition."
                ),
            )
