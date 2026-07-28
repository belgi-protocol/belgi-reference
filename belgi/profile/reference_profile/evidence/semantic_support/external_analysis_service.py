from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.evidence.subject_access import (
    subject_from_item,
    subject_identity_present,
    subject_structured_identity_present,
)
from belgi.profile.reference_profile.identifiers.environment import TOOLCHAIN_IDENTITY

__all__ = [
    "external_analysis_authoritative_subject_supported",
]


def _external_analysis_service_identity_present(subject: Mapping[str, object]) -> bool:
    if subject_identity_present(
        subject,
        str(TOOLCHAIN_IDENTITY),
        "toolchain_identity",
        "toolchainIdentity",
        "analysis_service",
        "analysisService",
        "service_identifier",
        "serviceIdentifier",
        "analyzer_identifier",
        "analyzerIdentifier",
        "analyzer_name",
        "analyzerName",
        "scanner_identifier",
        "scannerIdentifier",
    ):
        return True
    return subject_structured_identity_present(
        subject,
        field_names=(
            "analysis_service",
            "analysisService",
            "service",
            "analyzer",
            "scanner",
        ),
        member_keys=("identifier", "id", "uri", "name"),
    )


def _external_analysis_result_identity_present(subject: Mapping[str, object]) -> bool:
    if subject_identity_present(
        subject,
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
        return True
    return subject_structured_identity_present(
        subject,
        field_names=(
            "finding",
            "result",
            "analysis_result",
            "analysisResult",
            "scan",
            "report",
        ),
        member_keys=(
            "identifier",
            "id",
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
        ),
    )


def external_analysis_authoritative_subject_supported(item: object) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    return _external_analysis_service_identity_present(
        subject
    ) and _external_analysis_result_identity_present(subject)
