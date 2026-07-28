from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.evidence.subject_access import (
    subject_artifact_designator_present,
    subject_digest_anchor_present,
    subject_from_item,
    subject_mapping_view,
    subject_non_empty_text,
    subject_values,
)
from belgi.profile.reference_profile.identifiers.environment import REPOSITORY_IDENTITY

__all__ = [
    "repository_system_authoritative_subject_supported",
]


def _repository_identity_present(subject: Mapping[str, object]) -> bool:
    return any(
        subject_non_empty_text(value)
        for value in subject_values(
            subject,
            str(REPOSITORY_IDENTITY),
            "repository_identity",
            "repositoryIdentity",
            "repository_uri",
            "repositoryUri",
        )
    )


def _repository_anchor_value_present(value: object) -> bool:
    if subject_non_empty_text(value):
        return True
    if subject_artifact_designator_present(value) or subject_digest_anchor_present(
        value
    ):
        return True
    subject = subject_mapping_view(value)
    if subject is None:
        return False
    for key in (
        "revision_identifier",
        "source_state_identifier",
        "resolved_source_state",
        "tree_identifier",
        "snapshot_digest",
        "commit_sha",
        "commitSha",
        "treeSha",
        "repositoryObjectIdentifier",
        "repository_object_identifier",
        "objectIdentifier",
        "object_identifier",
        "repositoryDesignator",
        "repository_designator",
        "immutableDesignator",
        "immutable_designator",
    ):
        member = subject.get(key)
        if (
            subject_non_empty_text(member)
            or subject_artifact_designator_present(member)
            or subject_digest_anchor_present(member)
        ):
            return True
    return False


def _repository_anchor_present(subject: Mapping[str, object]) -> bool:
    for key in (
        "revision_identifier",
        "source_state_identifier",
        "resolved_source_state",
        "tree_identifier",
        "snapshot_digest",
        "commit_sha",
        "commitSha",
        "treeSha",
        "repositoryObjectIdentifier",
        "repository_object_identifier",
        "objectIdentifier",
        "object_identifier",
        "repositoryDesignator",
        "repository_designator",
        "immutableDesignator",
        "immutable_designator",
    ):
        if _repository_anchor_value_present(subject.get(key)):
            return True
    return False


def repository_system_authoritative_subject_supported(item: object) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    return _repository_identity_present(subject) and _repository_anchor_present(subject)
