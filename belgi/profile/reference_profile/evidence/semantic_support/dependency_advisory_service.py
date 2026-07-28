from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.evidence.subject_access import (
    subject_from_item,
    subject_identity_present,
    subject_structured_identity_present,
)

__all__ = [
    "dependency_advisory_authoritative_subject_supported",
]


def _dependency_advisory_source_identity_present(subject: Mapping[str, object]) -> bool:
    if subject_identity_present(
        subject,
        "advisory_source",
        "advisorySource",
        "advisory_source_identifier",
        "advisorySourceIdentifier",
        "advisory_dataset",
        "advisoryDataset",
        "dataset_identifier",
        "datasetIdentifier",
        "feed_identifier",
        "feedIdentifier",
    ):
        return True
    return subject_structured_identity_present(
        subject,
        field_names=("advisory_source", "advisorySource", "dataset", "feed"),
        member_keys=(
            "identifier",
            "id",
            "uri",
            "name",
            "dataset_identifier",
            "datasetIdentifier",
            "feed_identifier",
            "feedIdentifier",
        ),
    )


def _dependency_advisory_anchor_present(subject: Mapping[str, object]) -> bool:
    if subject_identity_present(
        subject,
        "advisory_identifier",
        "advisory_id",
        "advisoryId",
        "vulnerability_identifier",
        "vulnerability_id",
        "vulnerabilityId",
        "cve",
        "ghsa",
        "package_url",
        "packageUrl",
        "purl",
        "dependency_coordinate",
        "dependencyCoordinate",
        "dependency_name",
        "dependencyName",
        "package_name",
        "packageName",
    ):
        return True
    return subject_structured_identity_present(
        subject,
        field_names=("advisory", "vulnerability", "dependency", "package", "finding"),
        member_keys=(
            "identifier",
            "id",
            "advisory_id",
            "advisoryId",
            "vulnerability_id",
            "vulnerabilityId",
            "cve",
            "ghsa",
            "package_url",
            "packageUrl",
            "purl",
            "dependency_coordinate",
            "dependencyCoordinate",
            "dependency_name",
            "dependencyName",
            "package_name",
            "packageName",
        ),
    )


def dependency_advisory_authoritative_subject_supported(item: object) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    return _dependency_advisory_source_identity_present(
        subject
    ) and _dependency_advisory_anchor_present(subject)
