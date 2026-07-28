from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier.json_representation import (
    JSONRepresentationOutcome,
    TrustedJSONRole,
    validate_carrier_json,
    validate_json_representation,
)
from belgi.replay.lifting.exceptions import ParseFailureError

__all__ = [
    "load_carrier_json_object_from_outcome",
    "load_member_json_object",
    "load_trusted_carrier_json_object",
    "require_string",
]


def load_carrier_json_object_from_outcome(
    *,
    outcome: JSONRepresentationOutcome,
    description: str,
) -> Mapping[str, object]:
    if not outcome.accepted:
        if outcome.schema_issues:
            issue = next(
                (
                    candidate
                    for candidate in outcome.schema_issues
                    if candidate.keyword == "const" and candidate.path == "$.kind"
                ),
                outcome.schema_issues[0],
            )
            issue_path = (
                f"{description}{issue.path[1:]}"
                if issue.path.startswith("$")
                else issue.path
            )
            raise ParseFailureError(
                message=f"{description} invalid at {issue_path}: {issue.message}"
            )
        raise ParseFailureError(
            message=(
                f"{description} representation rejected at "
                f"{outcome.stage}: {outcome.result_code}"
            )
        )
    if not isinstance(outcome.value, dict):
        raise ParseFailureError(message=f"{description} must be a JSON object")
    return outcome.value


def load_member_json_object(
    *,
    octets: bytes,
    description: str,
) -> Mapping[str, object]:
    return load_carrier_json_object_from_outcome(
        outcome=validate_json_representation(octets),
        description=description,
    )


def load_trusted_carrier_json_object(
    *,
    octets: bytes,
    description: str,
    trusted_role: TrustedJSONRole,
) -> Mapping[str, object]:
    return load_carrier_json_object_from_outcome(
        outcome=validate_carrier_json(octets, trusted_role=trusted_role),
        description=description,
    )


def require_string(*, obj: Mapping[str, object], key: str, description: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        raise ParseFailureError(
            message=f"{description} requires a non-empty string field '{key}'",
        )
    return value
