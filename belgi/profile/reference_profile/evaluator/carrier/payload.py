from __future__ import annotations

from belgi.profile.edition import (
    CompanionIdentifier,
    Digest,
    EditionKind,
    ExactEditionBinding,
    ImmutableDesignator,
    ProfileIdentifier,
    VersionDesignator,
    companion_edition_binding,
    external_edition_binding,
    profile_edition_binding,
)
from belgi.profile.governance import (
    AuthorityLevelId,
    BindingKindId,
    ConditionId,
    EnvironmentTermId,
    EvidenceKindId,
    EvidenceSourceClassId,
    ReplayPolicyId,
    ToolchainSetId,
)
from belgi.profile.reference_profile.declarations import (
    ChangeBasisDeclaration,
    EnvironmentCompatibilityDeclaration,
    EnvironmentRequirement,
    EvidenceOutcome,
    EvidencePresenceDeclaration,
    OutcomePolicyDeclaration,
    ProfileConditionDeclaration,
    RequiredEvidenceBinding,
    ReviewPolicyDeclaration,
    change_basis_declaration,
)

from .parameters import (
    JsonCompatible,
    reference_profile_optional_int_payload,
    reference_profile_optional_numeric_payload,
    reference_profile_optional_severity_payload,
    reference_profile_required_bool_payload,
    reference_profile_required_int_payload,
    reference_profile_required_string_payload,
    reference_profile_required_string_tuple_payload,
)

__all__ = [
    "reference_profile_declaration_from_payload",
    "reference_profile_declaration_payload",
]


def reference_profile_declaration_payload(
    *,
    declaration: ProfileConditionDeclaration,
) -> JsonCompatible:
    if isinstance(declaration, ChangeBasisDeclaration):
        return {
            "kind": "change-basis",
            "requireProposalIdentifier": declaration.require_proposal_identifier,
            "requireBaselineIdentifier": declaration.require_baseline_identifier,
            "requireProposalSourceState": declaration.require_proposal_source_state,
            "requireBaselineSourceState": declaration.require_baseline_source_state,
            "replayRelevantDependencies": [
                _exact_edition_binding_payload(binding=binding)
                for binding in declaration.replay_relevant_dependencies
            ],
        }
    if isinstance(declaration, EvidencePresenceDeclaration):
        return {
            "kind": "evidence-presence",
            "requiredBindings": [
                _required_binding_payload(binding=binding)
                for binding in declaration.required_bindings
            ],
            "requireInterpretableBindings": declaration.require_interpretable_bindings,
            "replayRelevantDependencies": [
                _exact_edition_binding_payload(binding=binding)
                for binding in declaration.replay_relevant_dependencies
            ],
        }
    if isinstance(declaration, OutcomePolicyDeclaration):
        return {
            "kind": "outcome-policy",
            "requiredBindings": [
                _required_binding_payload(binding=binding)
                for binding in declaration.required_bindings
            ],
            "acceptedOutcomes": [
                outcome.value for outcome in declaration.accepted_outcomes
            ],
            "minimumNumericValue": declaration.minimum_numeric_value,
            "maximumNumericValue": declaration.maximum_numeric_value,
            "maximumSeverity": (
                None
                if declaration.maximum_severity is None
                else declaration.maximum_severity.value
            ),
            "maximumFailedCases": declaration.maximum_failed_cases,
            "replayRelevantDependencies": [
                _exact_edition_binding_payload(binding=binding)
                for binding in declaration.replay_relevant_dependencies
            ],
        }
    if isinstance(declaration, ReviewPolicyDeclaration):
        return {
            "kind": "review-policy",
            "requiredBindings": [
                _required_binding_payload(binding=binding)
                for binding in declaration.required_bindings
            ],
            "minimumApprovals": declaration.minimum_approvals,
            "allowBlockingReviews": declaration.allow_blocking_reviews,
            "replayRelevantDependencies": [
                _exact_edition_binding_payload(binding=binding)
                for binding in declaration.replay_relevant_dependencies
            ],
        }
    return {
        "kind": "environment-compatibility",
        "requiredBindings": [
            _required_binding_payload(binding=binding)
            for binding in declaration.required_bindings
        ],
        "requiredTerms": [
            _environment_requirement_payload(requirement=requirement)
            for requirement in declaration.required_terms
        ],
        "acceptedToolchainSets": [
            str(toolchain_set) for toolchain_set in declaration.accepted_toolchain_sets
        ],
        "equivalenceBasisIdentifiers": list(declaration.equivalence_basis_identifiers),
        "replayPolicy": str(declaration.replay_policy),
        "replayRelevantDependencies": [
            _exact_edition_binding_payload(binding=binding)
            for binding in declaration.replay_relevant_dependencies
        ],
    }


def reference_profile_declaration_from_payload(
    *,
    condition_identifier: str,
    payload: dict[str, JsonCompatible],
) -> ProfileConditionDeclaration:
    kind = payload.get("kind")
    replay_relevant_dependencies = _exact_edition_bindings_from_payload(
        payload=payload.get("replayRelevantDependencies")
    )
    if kind == "change-basis":
        return change_basis_declaration(
            require_proposal_identifier=reference_profile_required_bool_payload(
                payload["requireProposalIdentifier"]
            ),
            require_baseline_identifier=reference_profile_required_bool_payload(
                payload["requireBaselineIdentifier"]
            ),
            require_proposal_source_state=reference_profile_required_bool_payload(
                payload["requireProposalSourceState"]
            ),
            require_baseline_source_state=reference_profile_required_bool_payload(
                payload["requireBaselineSourceState"]
            ),
            replay_relevant_dependencies=replay_relevant_dependencies,
        )
    if kind == "evidence-presence":
        return EvidencePresenceDeclaration(
            condition_id=ConditionId(condition_identifier),
            required_bindings=_required_bindings_from_payload(
                payload=payload.get("requiredBindings")
            ),
            require_interpretable_bindings=reference_profile_required_bool_payload(
                payload["requireInterpretableBindings"]
            ),
            replay_relevant_dependencies=replay_relevant_dependencies,
        )
    if kind == "outcome-policy":
        return OutcomePolicyDeclaration(
            condition_id=ConditionId(condition_identifier),
            required_bindings=_required_bindings_from_payload(
                payload=payload.get("requiredBindings")
            ),
            accepted_outcomes=tuple(
                EvidenceOutcome(outcome)
                for outcome in reference_profile_required_string_tuple_payload(
                    payload=payload.get("acceptedOutcomes")
                )
            ),
            minimum_numeric_value=reference_profile_optional_numeric_payload(
                payload.get("minimumNumericValue")
            ),
            maximum_numeric_value=reference_profile_optional_numeric_payload(
                payload.get("maximumNumericValue")
            ),
            maximum_severity=reference_profile_optional_severity_payload(
                payload.get("maximumSeverity")
            ),
            maximum_failed_cases=reference_profile_optional_int_payload(
                payload.get("maximumFailedCases")
            ),
            replay_relevant_dependencies=replay_relevant_dependencies,
        )
    if kind == "review-policy":
        return ReviewPolicyDeclaration(
            condition_id=ConditionId(condition_identifier),
            required_bindings=_required_bindings_from_payload(
                payload=payload.get("requiredBindings")
            ),
            minimum_approvals=reference_profile_required_int_payload(
                payload.get("minimumApprovals")
            ),
            allow_blocking_reviews=reference_profile_required_bool_payload(
                payload["allowBlockingReviews"]
            ),
            replay_relevant_dependencies=replay_relevant_dependencies,
        )
    if kind == "environment-compatibility":
        return EnvironmentCompatibilityDeclaration(
            condition_id=ConditionId(condition_identifier),
            required_bindings=_required_bindings_from_payload(
                payload=payload.get("requiredBindings")
            ),
            required_terms=_environment_requirements_from_payload(
                payload=payload.get("requiredTerms")
            ),
            accepted_toolchain_sets=tuple(
                ToolchainSetId(toolchain_set)
                for toolchain_set in reference_profile_required_string_tuple_payload(
                    payload=payload.get("acceptedToolchainSets")
                )
            ),
            equivalence_basis_identifiers=reference_profile_required_string_tuple_payload(
                payload=payload.get("equivalenceBasisIdentifiers")
            ),
            replay_policy=ReplayPolicyId(
                reference_profile_required_string_payload(payload["replayPolicy"])
            ),
            replay_relevant_dependencies=replay_relevant_dependencies,
        )
    raise ValueError(
        "unsupported reference-profile declaration payload kind: "
        f"{kind!r} for {condition_identifier}."
    )


def _required_binding_payload(
    *,
    binding: RequiredEvidenceBinding,
) -> JsonCompatible:
    return {
        "evidenceKind": str(binding.evidence_kind),
        "bindingKind": str(binding.binding_kind),
        "minimumCount": binding.minimum_count,
        "minimumAuthority": str(binding.minimum_authority),
        "allowedSourceClasses": [
            str(source_class) for source_class in binding.allowed_source_classes
        ],
        "exactEvidenceIdentifiers": list(binding.exact_evidence_identifiers),
    }


def _required_bindings_from_payload(
    *,
    payload: object,
) -> tuple[RequiredEvidenceBinding, ...]:
    if not isinstance(payload, list):
        raise ValueError("requiredBindings payload must be a JSON array.")
    return tuple(
        _required_binding_from_payload(binding_payload=binding_payload)
        for binding_payload in payload
    )


def _required_binding_from_payload(
    *,
    binding_payload: object,
) -> RequiredEvidenceBinding:
    if not isinstance(binding_payload, dict):
        raise ValueError("required binding payload must be a JSON object.")
    return RequiredEvidenceBinding(
        evidence_kind=EvidenceKindId(
            reference_profile_required_string_payload(binding_payload["evidenceKind"])
        ),
        binding_kind=BindingKindId(
            reference_profile_required_string_payload(binding_payload["bindingKind"])
        ),
        minimum_count=reference_profile_required_int_payload(
            binding_payload["minimumCount"]
        ),
        minimum_authority=AuthorityLevelId(
            reference_profile_required_string_payload(
                binding_payload["minimumAuthority"]
            )
        ),
        allowed_source_classes=tuple(
            EvidenceSourceClassId(source_class)
            for source_class in reference_profile_required_string_tuple_payload(
                payload=binding_payload.get("allowedSourceClasses")
            )
        ),
        exact_evidence_identifiers=reference_profile_required_string_tuple_payload(
            payload=binding_payload.get("exactEvidenceIdentifiers")
        ),
    )


def _environment_requirement_payload(
    *,
    requirement: EnvironmentRequirement,
) -> JsonCompatible:
    return {
        "termId": str(requirement.term_id),
        "acceptedValues": list(requirement.accepted_values),
    }


def _environment_requirements_from_payload(
    *,
    payload: object,
) -> tuple[EnvironmentRequirement, ...]:
    if not isinstance(payload, list):
        raise ValueError("requiredTerms payload must be a JSON array.")
    requirements: list[EnvironmentRequirement] = []
    for requirement_payload in payload:
        if not isinstance(requirement_payload, dict):
            raise ValueError("environment requirement payload must be a JSON object.")
        requirements.append(
            EnvironmentRequirement(
                term_id=EnvironmentTermId(
                    reference_profile_required_string_payload(
                        requirement_payload["termId"]
                    )
                ),
                accepted_values=reference_profile_required_string_tuple_payload(
                    payload=requirement_payload.get("acceptedValues")
                ),
            )
        )
    return tuple(requirements)


def _exact_edition_binding_payload(
    *,
    binding: ExactEditionBinding,
) -> JsonCompatible:
    return {
        "kind": binding.kind.value,
        "familyIdentifier": str(binding.family_identifier),
        "versionDesignator": str(binding.version_designator),
        "immutableDesignator": {
            "uri": binding.immutable_designator.uri,
            "digest": {
                "algorithmId": binding.immutable_designator.digest.algorithm_id,
                "digestValue": binding.immutable_designator.digest.digest_value,
            },
        },
    }


def _exact_edition_bindings_from_payload(
    *,
    payload: object,
) -> tuple[ExactEditionBinding, ...]:
    if payload is None:
        return ()
    if not isinstance(payload, list):
        raise ValueError("replayRelevantDependencies payload must be a JSON array.")
    return tuple(
        _exact_edition_binding_from_payload(binding_payload=binding_payload)
        for binding_payload in payload
    )


def _exact_edition_binding_from_payload(
    *,
    binding_payload: object,
) -> ExactEditionBinding:
    if not isinstance(binding_payload, dict):
        raise ValueError("exact-edition binding payload must be a JSON object.")
    kind = EditionKind(
        reference_profile_required_string_payload(binding_payload["kind"])
    )
    family_identifier = reference_profile_required_string_payload(
        binding_payload["familyIdentifier"]
    )
    version = VersionDesignator(
        reference_profile_required_string_payload(binding_payload["versionDesignator"])
    )
    designator = _immutable_designator_from_payload(
        payload=binding_payload.get("immutableDesignator")
    )
    if kind is EditionKind.PROFILE:
        return profile_edition_binding(
            identifier=ProfileIdentifier(family_identifier),
            version=version,
            immutable_designator=designator,
        )
    if kind is EditionKind.COMPANION:
        return companion_edition_binding(
            identifier=CompanionIdentifier(family_identifier),
            version=version,
            immutable_designator=designator,
        )
    return external_edition_binding(
        identifier=family_identifier,
        version=version,
        immutable_designator=designator,
    )


def _immutable_designator_from_payload(
    *,
    payload: object,
) -> ImmutableDesignator:
    if not isinstance(payload, dict):
        raise ValueError("immutableDesignator payload must be a JSON object.")
    digest_payload = payload.get("digest")
    if not isinstance(digest_payload, dict):
        raise ValueError("immutableDesignator.digest payload must be a JSON object.")
    return ImmutableDesignator(
        uri=reference_profile_required_string_payload(payload["uri"]),
        digest=Digest(
            algorithm_id=reference_profile_required_string_payload(
                digest_payload["algorithmId"]
            ),
            digest_value=reference_profile_required_string_payload(
                digest_payload["digestValue"]
            ),
        ),
    )
