from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.evidence.subject_access import (
    subject_artifact_designator_present,
    subject_digest_anchor_present,
    subject_from_item,
    subject_mapping_view,
    subject_non_empty_text,
)

__all__ = [
    "artifact_store_authoritative_subject_supported",
]


def _artifact_identity_present(subject: Mapping[str, object]) -> bool:
    for key in (
        "artifactDesignator",
        "artifact_designator",
        "artifactIdentity",
        "artifact_identity",
        "artifact",
        "designator",
    ):
        if subject_artifact_designator_present(subject.get(key)):
            return True

    if not subject_non_empty_text(
        subject.get("artifactId")
        or subject.get("artifact_id")
        or subject.get("artifactUri")
        or subject.get("artifact_uri")
        or subject.get("uri")
        or subject.get("path")
    ):
        return False

    for key in ("artifactDigest", "artifact_digest", "digest"):
        if subject_digest_anchor_present(subject.get(key)):
            return True
    return subject_digest_anchor_present(subject)


def _origin_linkage_present(subject: Mapping[str, object]) -> bool:
    for key in (
        "originLinkage",
        "origin_linkage",
        "artifactOrigin",
        "artifact_origin",
        "provenance",
        "provenanceRecord",
        "provenance_record",
        "sourceRun",
        "source_run",
        "producer",
        "producedBy",
        "produced_by",
    ):
        value = subject.get(key)
        mapping = subject_mapping_view(value)
        if mapping is None:
            continue
        if _origin_linkage_mapping_supported(mapping):
            return True
    return False


def _origin_linkage_mapping_supported(mapping: Mapping[str, object]) -> bool:
    for key in (
        "run_identity",
        "runIdentity",
        "run_id",
        "runId",
        "source_reference",
        "sourceReference",
        "commit_sha",
        "commitSha",
        "tree_sha",
        "treeSha",
        "attestation",
        "attestationDigest",
        "attestation_digest",
        "provenanceDigest",
        "provenance_digest",
    ):
        member = mapping.get(key)
        if (
            subject_non_empty_text(member)
            or subject_artifact_designator_present(member)
            or subject_digest_anchor_present(member)
        ):
            return True
    return False


def artifact_store_authoritative_subject_supported(item: object) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    return _artifact_identity_present(subject) and _origin_linkage_present(subject)
