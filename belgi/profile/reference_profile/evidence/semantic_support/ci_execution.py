from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.companions.ci_trust.edition import (
    COMPANION_IDENTIFIER as CI_TRUST_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.ci_trust.identifiers.environment import (
    RUN_IDENTITY,
    SOURCE_REFERENCE_IDENTITY,
    WORKFLOW_DEFINITION_IDENTITY,
)
from belgi.profile.companions.ci_trust.identifiers.sources import STATUS_SUMMARY
from belgi.profile.companions.ci_trust.supported import (
    SUPPORTED_CI_ENVIRONMENT_TERMS,
    SUPPORTED_CI_SOURCE_MATERIAL_ROLES,
)
from belgi.profile.reference_profile.config.exact_editions import (
    resolve_reference_profile_companion_binding,
)
from belgi.profile.reference_profile.evidence.subject_access import (
    subject_artifact_designator_present,
    subject_digest_anchor_present,
    subject_field,
    subject_from_item,
    subject_identity_anchor_present,
    subject_mapping_view,
    subject_values,
)
from belgi.substrate.git.identity import is_full_git_object_id

__all__ = [
    "ci_execution_authoritative_subject_supported",
]

_CI_SOURCE_ROLE_IDS = frozenset(
    str(role) for role in SUPPORTED_CI_SOURCE_MATERIAL_ROLES
)
_CI_ENVIRONMENT_TERM_IDS = frozenset(
    str(term) for term in SUPPORTED_CI_ENVIRONMENT_TERMS
)
_CI_SOURCE_ROLE_PREFIX = "belgi.ci.source."
_CI_ENVIRONMENT_TERM_PREFIX = "belgi.ci.environment."
_RUN_IDENTITY_KEYS = (
    str(RUN_IDENTITY),
    "run_identity",
    "runIdentity",
    "run_id",
    "runId",
    "ci_run_id",
    "ciRunId",
    "workflow_run_id",
    "workflowRunId",
    "execution_id",
    "executionId",
)
_SOURCE_REFERENCE_KEYS = (
    str(SOURCE_REFERENCE_IDENTITY),
    "source_reference_identity",
    "sourceReferenceIdentity",
    "source_reference",
    "sourceReference",
    "source_state",
    "sourceState",
    "source_revision",
    "sourceRevision",
    "source_sha",
    "sourceSha",
    "commit_sha",
    "commitSha",
    "tree_sha",
    "treeSha",
    "source_digest",
    "sourceDigest",
    "immutable_source_reference",
    "immutableSourceReference",
)


def _ci_execution_role_is_decisive(subject: Mapping[str, object]) -> bool:
    for key in (
        "sourceMaterialRole",
        "source_material_role",
        "sourceRole",
        "source_role",
        "ciSourceRole",
        "ci_source_role",
    ):
        value = subject.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            return False
        if value == str(STATUS_SUMMARY):
            return False
    return True


def _ci_execution_identity_present(
    subject: Mapping[str, object],
    *keys: str,
) -> bool:
    return any(
        subject_identity_anchor_present(value)
        for value in subject_values(subject, *keys)
    )


def _ci_execution_run_identity_present(subject: Mapping[str, object]) -> bool:
    if _ci_execution_identity_present(subject, *_RUN_IDENTITY_KEYS):
        return True
    return _ci_execution_structured_identity_present(
        subject,
        field_names=("run", "ci_run", "ciRun", "execution"),
        member_keys=("identifier", "id", "run_id", "runId"),
    )


def _ci_execution_workflow_definition_identity_present(
    subject: Mapping[str, object],
) -> bool:
    if _ci_execution_identity_present(
        subject,
        str(WORKFLOW_DEFINITION_IDENTITY),
        "workflow_definition_identity",
        "workflowDefinitionIdentity",
        "workflow_definition",
        "workflowDefinition",
        "workflow_id",
        "workflowId",
        "workflow_ref",
        "workflowRef",
        "workflow_sha",
        "workflowSha",
    ):
        return True
    return _ci_execution_structured_identity_present(
        subject,
        field_names=("workflow", "workflow_definition", "workflowDefinition"),
        member_keys=(
            "identifier",
            "id",
            "uri",
            "digest",
            "definition_digest",
            "definitionDigest",
            "workflow_sha",
            "workflowSha",
        ),
    )


def _ci_execution_source_reference_identity_present(
    subject: Mapping[str, object],
) -> bool:
    if any(
        _ci_execution_immutable_source_value(value)
        for value in subject_values(subject, *_SOURCE_REFERENCE_KEYS)
    ):
        return True
    for field_name in ("source", "source_reference", "sourceReference", "revision"):
        mapping = subject_mapping_view(subject.get(field_name))
        if mapping is None:
            continue
        for member_key in (
            "identifier",
            "id",
            "uri",
            "digest",
            "commit_sha",
            "commitSha",
            "tree_sha",
            "treeSha",
            "source_sha",
            "sourceSha",
        ):
            if _ci_execution_immutable_source_value(mapping.get(member_key)):
                return True
    return False


def _ci_execution_immutable_source_value(value: object) -> bool:
    if subject_artifact_designator_present(value) or subject_digest_anchor_present(
        value
    ):
        return True
    if not isinstance(value, str):
        return False
    return is_full_git_object_id(value)


def _ci_execution_structured_identity_present(
    subject: Mapping[str, object],
    *,
    field_names: tuple[str, ...],
    member_keys: tuple[str, ...],
) -> bool:
    for field_name in field_names:
        mapping = subject_mapping_view(subject.get(field_name))
        if mapping is None:
            continue
        for member_key in member_keys:
            if subject_identity_anchor_present(mapping.get(member_key)):
                return True
    return False


def _ci_execution_artifact_or_report_referenced(
    subject: Mapping[str, object],
) -> bool:
    for key in (
        "artifact",
        "artifactDesignator",
        "artifact_designator",
        "artifactIdentity",
        "artifact_identity",
        "artifactUri",
        "artifact_uri",
        "artifactUrl",
        "artifact_url",
        "artifactPath",
        "artifact_path",
        "path",
        "filename",
        "fileName",
        "cacheKey",
        "cache_key",
        "packageMemberName",
        "package_member_name",
        "report",
        "reportDesignator",
        "report_designator",
        "reportId",
        "report_id",
        "reportPath",
        "report_path",
        "reportUri",
        "report_uri",
    ):
        if subject.get(key) is not None:
            return True
    return False


def _ci_execution_artifact_origin_linkage_present(
    subject: Mapping[str, object],
) -> bool:
    for key in (
        "artifactOrigin",
        "artifact_origin",
        "originLinkage",
        "origin_linkage",
        "provenance",
        "provenanceRecord",
        "provenance_record",
    ):
        if _ci_execution_origin_value_supported(
            value=subject.get(key),
            subject=subject,
        ):
            return True
    return False


def _ci_execution_origin_value_supported(
    *,
    value: object,
    subject: Mapping[str, object],
) -> bool:
    mapping = subject_mapping_view(value)
    if mapping is None:
        return False
    run_identities = subject_values(subject, *_RUN_IDENTITY_KEYS)
    for key in (
        "run_identity",
        "runIdentity",
        "run_id",
        "runId",
        "workflow_run_id",
        "workflowRunId",
    ):
        member = mapping.get(key)
        if member is not None and any(
            member == identity for identity in run_identities
        ):
            return True
    for key in (
        "attestation",
        "attestationDigest",
        "attestation_digest",
        "provenanceDigest",
        "provenance_digest",
    ):
        member = mapping.get(key)
        if subject_artifact_designator_present(member) or subject_digest_anchor_present(
            member
        ):
            return True
    return False


def _ci_execution_artifact_origin_requirement_satisfied(
    subject: Mapping[str, object],
    *,
    companion_vocabulary_used: bool,
) -> bool:
    if (
        not companion_vocabulary_used
        and not _ci_execution_artifact_or_report_referenced(subject)
    ):
        return True
    return _ci_execution_artifact_origin_linkage_present(subject)


def _ci_companion_dependency_selected(*, condition: object | None) -> bool:
    declaration = condition
    if declaration is not None:
        nested = subject_field(declaration, "profile_declaration", "declaration")
        if nested is not None:
            declaration = nested
    dependencies = subject_field(declaration, "replay_relevant_dependencies")
    if not isinstance(dependencies, tuple):
        return False
    expected = resolve_reference_profile_companion_binding(
        companion_identifier=str(CI_TRUST_COMPANION_IDENTIFIER),
    )
    return expected in dependencies


def _ci_companion_tokens_state(*, subject: Mapping[str, object]) -> tuple[bool, bool]:
    companion_vocabulary_used = False
    for key in subject:
        if key.startswith(_CI_ENVIRONMENT_TERM_PREFIX):
            companion_vocabulary_used = True
            if key not in _CI_ENVIRONMENT_TERM_IDS:
                return True, False
    for key in (
        "sourceMaterialRole",
        "source_material_role",
        "sourceRole",
        "source_role",
        "ciSourceRole",
        "ci_source_role",
    ):
        value = subject.get(key)
        if not isinstance(value, str):
            continue
        if value.startswith(_CI_SOURCE_ROLE_PREFIX):
            companion_vocabulary_used = True
            if value not in _CI_SOURCE_ROLE_IDS:
                return True, False
    for field_name in ("environment_terms", "environment"):
        environment = subject_mapping_view(subject.get(field_name))
        if environment is None:
            continue
        for key in environment:
            if key.startswith(_CI_ENVIRONMENT_TERM_PREFIX):
                companion_vocabulary_used = True
                if key not in _CI_ENVIRONMENT_TERM_IDS:
                    return True, False
    return companion_vocabulary_used, True


def ci_execution_authoritative_subject_supported(
    item: object,
    *,
    condition: object | None = None,
) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    companion_vocabulary_used, companion_tokens_supported = _ci_companion_tokens_state(
        subject=subject
    )
    return (
        companion_tokens_supported
        and (
            not companion_vocabulary_used
            or _ci_companion_dependency_selected(condition=condition)
        )
        and _ci_execution_role_is_decisive(subject)
        and _ci_execution_run_identity_present(subject)
        and _ci_execution_workflow_definition_identity_present(subject)
        and _ci_execution_source_reference_identity_present(subject)
        and _ci_execution_artifact_origin_requirement_satisfied(
            subject,
            companion_vocabulary_used=companion_vocabulary_used,
        )
    )
