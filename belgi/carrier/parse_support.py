"""Shared value-construction helpers for carrier-owned JSON documents."""

from __future__ import annotations

from collections.abc import Mapping

from .inventory import Digest, ImmutableDesignator


def require_mapping_object(
    *,
    value: object,
    label: str,
    error_type: type[Exception],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise error_type(f"{label} must be an object.")
    return value


def require_allowed_keys(
    *,
    payload: Mapping[str, object],
    label: str,
    allowed_keys: frozenset[str],
    error_type: type[Exception],
) -> None:
    unexpected = sorted(key for key in payload if key not in allowed_keys)
    if unexpected:
        raise error_type(
            f"{label} contains unsupported fields: {', '.join(unexpected)}."
        )


def require_non_empty_text(
    *,
    value: object,
    label: str,
    error_type: type[Exception],
) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise error_type(f"{label} must be a non-empty string.")
    return value


def _parse_digest_object(
    *,
    value: object,
    label: str,
    error_type: type[Exception],
) -> Digest:
    payload = require_mapping_object(
        value=value,
        label=label,
        error_type=error_type,
    )
    require_allowed_keys(
        payload=payload,
        label=label,
        allowed_keys=frozenset({"algorithmId", "digestValue"}),
        error_type=error_type,
    )
    return Digest(
        algorithm_id=require_non_empty_text(
            value=payload.get("algorithmId"),
            label=f"{label}.algorithmId",
            error_type=error_type,
        ),
        digest_value=require_non_empty_text(
            value=payload.get("digestValue"),
            label=f"{label}.digestValue",
            error_type=error_type,
        ),
    )


def parse_immutable_designator_object(
    *,
    value: object,
    label: str,
    error_type: type[Exception],
) -> ImmutableDesignator:
    payload = require_mapping_object(
        value=value,
        label=label,
        error_type=error_type,
    )
    require_allowed_keys(
        payload=payload,
        label=label,
        allowed_keys=frozenset({"uri", "digest"}),
        error_type=error_type,
    )
    return ImmutableDesignator(
        uri=require_non_empty_text(
            value=payload.get("uri"),
            label=f"{label}.uri",
            error_type=error_type,
        ),
        digest=_parse_digest_object(
            value=payload.get("digest"),
            label=f"{label}.digest",
            error_type=error_type,
        ),
    )
