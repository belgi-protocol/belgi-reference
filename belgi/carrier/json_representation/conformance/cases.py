from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier.json_representation.model import JSONRepresentationOutcome
from belgi.carrier.json_representation.schemas import CarrierSchemaGraph
from belgi.carrier.json_representation.validation import (
    validate_carrier_json,
    validate_json_representation,
)

from .inputs import required_json_representation_corpus_text


def observe_json_representation_case(
    *,
    case: Mapping[str, object],
) -> JSONRepresentationOutcome:
    operation = required_json_representation_corpus_text(case, field="operation")
    candidate = _json_case_required_hex_bytes(case, field="inputHex")
    if operation == "representation-validate":
        return validate_json_representation(candidate)
    if operation not in {"schema-validate", "canonicalize"}:
        raise ValueError(f"Unknown JSON representation operation: {operation!r}.")
    unavailable = _json_case_optional_text_set(case, field="unavailableDependencies")
    return validate_carrier_json(
        candidate,
        trusted_role=required_json_representation_corpus_text(
            case, field="trustedRole"
        ),
        canonicalize=operation == "canonicalize",
        schema_graph=CarrierSchemaGraph.from_package(
            unavailable_schema_names=unavailable
        ),
    )


def json_representation_observation_document(
    *,
    outcome: JSONRepresentationOutcome,
) -> dict[str, object]:
    document: dict[str, object] = {
        "accepted": outcome.accepted,
        "stage": outcome.stage,
        "resultCode": outcome.result_code,
    }
    if outcome.canonical_bytes is not None:
        document["canonicalHex"] = outcome.canonical_bytes.hex()
    return document


def _json_case_required_hex_bytes(
    payload: Mapping[str, object], *, field: str
) -> bytes:
    text = payload.get(field)
    if not isinstance(text, str):
        raise ValueError(f"JSON representation corpus {field!r} must be text.")
    if len(text) % 2 != 0 or any(
        character not in "0123456789abcdef" for character in text
    ):
        raise ValueError(
            f"JSON representation corpus {field!r} must be lowercase hexadecimal."
        )
    return bytes.fromhex(text)


def _json_case_optional_text_set(
    payload: Mapping[str, object], *, field: str
) -> frozenset[str]:
    value = payload.get(field, ())
    if not isinstance(value, (list, tuple)) or not all(
        isinstance(item, str) and item != "" for item in value
    ):
        raise ValueError(
            f"JSON representation corpus {field!r} must be an array of text."
        )
    return frozenset(value)


__all__ = [
    "json_representation_observation_document",
    "observe_json_representation_case",
]
