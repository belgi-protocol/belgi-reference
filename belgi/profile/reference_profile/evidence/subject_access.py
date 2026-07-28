from __future__ import annotations

from collections.abc import Mapping

__all__ = [
    "subject_artifact_designator_present",
    "subject_digest_anchor_present",
    "subject_field",
    "subject_from_item",
    "subject_identity_anchor_present",
    "subject_identity_present",
    "subject_mapping_lookup",
    "subject_mapping_view",
    "subject_non_empty_identifier",
    "subject_non_empty_text",
    "subject_structured_identity_present",
    "subject_values",
]


def subject_field(subject: object, *names: str) -> object | None:
    for name in names:
        if not hasattr(subject, name):
            continue
        value = getattr(subject, name)
        if callable(value):
            continue
        return value
    return None


def subject_mapping_view(value: object) -> Mapping[str, object] | None:
    if isinstance(value, Mapping):
        return value
    if not isinstance(value, tuple):
        return None
    mapping: dict[str, object] = {}
    for entry in value:
        if not isinstance(entry, tuple) or len(entry) != 2:
            return None
        key, member = entry
        if not isinstance(key, str):
            return None
        mapping[key] = member
    return mapping


def subject_mapping_lookup(mapping: Mapping[str, object], *keys: str) -> object | None:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def subject_values(subject: Mapping[str, object], *keys: str) -> tuple[object, ...]:
    values: list[object] = []
    for key in keys:
        if key in subject:
            values.append(subject[key])
    for field_name in ("environment_terms", "environment"):
        nested = subject_mapping_view(subject.get(field_name))
        if nested is None:
            continue
        for key in keys:
            if key in nested:
                values.append(nested[key])
    return tuple(values)


def subject_non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def subject_non_empty_identifier(value: object) -> bool:
    return subject_non_empty_text(value) or (
        isinstance(value, int) and not isinstance(value, bool)
    )


def subject_digest_anchor_present(value: object) -> bool:
    mapping = subject_mapping_view(value)
    if mapping is None:
        return False
    if subject_non_empty_text(mapping.get("algorithmId")) and subject_non_empty_text(
        mapping.get("digestValue")
    ):
        return True
    digest = subject_mapping_view(mapping.get("digest"))
    if digest is None:
        return False
    return subject_non_empty_text(digest.get("algorithmId")) and subject_non_empty_text(
        digest.get("digestValue")
    )


def subject_artifact_designator_present(value: object) -> bool:
    mapping = subject_mapping_view(value)
    if mapping is None:
        return False
    return subject_non_empty_text(
        subject_mapping_lookup(mapping, "uri", "artifactUri", "artifact_uri", "path")
    ) and subject_digest_anchor_present(mapping)


def subject_identity_anchor_present(value: object) -> bool:
    if subject_non_empty_identifier(value):
        return True
    if subject_artifact_designator_present(value) or subject_digest_anchor_present(
        value
    ):
        return True
    mapping = subject_mapping_view(value)
    if mapping is None:
        return False
    for key in (
        "identifier",
        "id",
        "uri",
        "name",
        "digest",
        "dataset_identifier",
        "datasetIdentifier",
        "feed_identifier",
        "feedIdentifier",
        "advisory_id",
        "advisoryId",
        "vulnerability_id",
        "vulnerabilityId",
        "cve",
        "ghsa",
        "package_url",
        "packageUrl",
        "purl",
        "analysis_run_id",
        "analysisRunId",
        "scan_id",
        "scanId",
        "report_id",
        "reportId",
        "result_id",
        "resultId",
        "finding_id",
        "findingId",
        "issue_id",
        "issueId",
        "rule_id",
        "ruleId",
        "check_id",
        "checkId",
    ):
        member = mapping.get(key)
        if member is None:
            continue
        if (
            subject_non_empty_identifier(member)
            or subject_artifact_designator_present(member)
            or subject_digest_anchor_present(member)
        ):
            return True
    return False


def subject_identity_present(subject: Mapping[str, object], *keys: str) -> bool:
    return any(
        subject_identity_anchor_present(value)
        for value in subject_values(subject, *keys)
    )


def subject_structured_identity_present(
    subject: Mapping[str, object],
    *,
    field_names: tuple[str, ...],
    member_keys: tuple[str, ...],
) -> bool:
    for field_name in field_names:
        value = subject.get(field_name)
        if value is None:
            continue
        mapping = subject_mapping_view(value)
        if mapping is None:
            continue
        for member_key in member_keys:
            if subject_identity_anchor_present(mapping.get(member_key)):
                return True
    return False


def subject_from_item(item: object) -> Mapping[str, object] | None:
    return subject_mapping_view(subject_field(item, "subject"))
