"""Exact JSON carrier projection and acceptance for normative replay reports."""

from __future__ import annotations

from typing import Any

from belgi.carrier.json_representation import CarrierSchemaGraph, TrustedJSONRole

from .problems import MALFORMED_CLAIM_RECORD
from .report import ReplayReport

__all__ = [
    "replay_report_to_json_object",
    "validate_replay_report_document",
]


def replay_report_to_json_object(
    *,
    report: ReplayReport[Any],
) -> dict[str, object]:
    """Project one typed report onto the exact ReplayReport carrier surface."""

    document: dict[str, object] = {
        "status": str(report.status),
        "outcomeClass": str(report.outcome_class),
        "packageIdentifier": (
            None if report.package_identifier is None else report.package_identifier
        ),
        "problems": [
            {
                "type": str(problem.type),
                "title": problem.title,
                "detail": problem.detail,
                **(
                    {"relatedReference": str(problem.related_reference)}
                    if problem.related_reference is not None
                    else {}
                ),
            }
            for problem in report.problems
        ],
        "warnings": [
            {
                "type": str(warning.type),
                "title": warning.title,
                "detail": warning.detail,
            }
            for warning in report.warnings
        ],
    }
    if report.derived_verdict is not None:
        verdict = report.derived_verdict
        if (
            not isinstance(verdict, int)
            or isinstance(verdict, bool)
            or int(verdict) not in (0, 1)
        ):
            raise ValueError("ReplayReport derived verdict must be binary.")
        document["derivedVerdict"] = int(verdict)

    return validate_replay_report_document(
        document=document,
        label="ReplayReport carrier projection",
    )


def validate_replay_report_document(
    *,
    document: object,
    label: str,
) -> dict[str, object]:
    if not isinstance(document, dict):
        raise ValueError(f"{label} must be a JSON object")
    issues = CarrierSchemaGraph.from_package().validate(
        instance=document,
        trusted_role=TrustedJSONRole.REPLAY_REPORT,
        path="$",
    )
    if issues:
        rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in issues[:3])
        raise ValueError(f"{label} is invalid: {rendered}")
    _require_typed_report_invariants(document=document, label=label)
    return document


def _require_typed_report_invariants(
    *,
    document: dict[str, object],
    label: str,
) -> None:
    problems = document["problems"]
    if not isinstance(problems, list):
        raise AssertionError("ReplayReport schema admitted a non-list problems value")
    if document["status"] == "replayable":
        if problems:
            raise ValueError(f"{label} is invalid: replayable reports forbid problems")
        return
    if not problems:
        raise ValueError(
            f"{label} is invalid: non-replayable reports require at least one problem"
        )
    if document["packageIdentifier"] is None and not any(
        isinstance(problem, dict) and problem.get("type") == MALFORMED_CLAIM_RECORD
        for problem in problems
    ):
        raise ValueError(
            f"{label} is invalid: an unavailable package identifier requires a "
            "malformed-claim-record problem"
        )
