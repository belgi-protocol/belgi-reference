from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    ContentLocator,
    ContentLocatorMode,
    DeclarationParameter,
    JsonCompatible,
    MemberName,
    ParameterIdentifier,
)
from belgi.replay.lifting.exceptions import InduceFailureError, ParseFailureError
from belgi.replay.lifting.parsing import require_string

__all__ = [
    "content_locator_from_payload",
    "dependency_references_for_member_names",
    "json_compatible_value",
    "parse_declaration_parameters",
    "require_inline_json_object",
    "require_json_mapping",
]


def require_json_mapping(
    *,
    value: object,
    description: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ParseFailureError(message=f"{description} must be a JSON object")
    return value


def json_compatible_value(
    *,
    value: object,
    description: str,
) -> JsonCompatible:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [
            json_compatible_value(value=item, description=f"{description}[]")
            for item in value
        ]
    if isinstance(value, Mapping):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ParseFailureError(
                    message=f"{description} must use string object keys",
                )
            converted[key] = json_compatible_value(
                value=item,
                description=f"{description}.{key}",
            )
        return converted
    raise ParseFailureError(
        message=f"{description} must contain only JSON-compatible values",
    )


def parse_declaration_parameters(
    *,
    payload: object | None,
    description: str,
) -> tuple[DeclarationParameter, ...]:
    if payload is None:
        return ()
    if not isinstance(payload, list):
        raise ParseFailureError(message=f"{description} must be a JSON array")
    parameters: list[DeclarationParameter] = []
    seen: set[str] = set()
    for index, raw_parameter in enumerate(payload):
        parameter = require_json_mapping(
            value=raw_parameter,
            description=f"{description}[{index}]",
        )
        parameter_identifier = require_string(
            obj=parameter,
            key="parameterIdentifier",
            description=f"{description}[{index}]",
        )
        if parameter_identifier in seen:
            raise ParseFailureError(
                message=f"{description} contains duplicate parameter {parameter_identifier!r}",
            )
        if "value" not in parameter:
            raise ParseFailureError(
                message=f"{description}[{index}] requires field 'value'",
            )
        parameters.append(
            DeclarationParameter.from_value(
                parameter_identifier=ParameterIdentifier(parameter_identifier),
                value=json_compatible_value(
                    value=parameter["value"],
                    description=f"{description}[{index}].value",
                ),
            )
        )
        seen.add(parameter_identifier)
    return tuple(parameters)


def dependency_references_for_member_names(
    *,
    member_names: tuple[MemberName, ...],
    claim_record: ClaimRecord,
) -> tuple[CanonicalReference, ...]:
    ordered: list[CanonicalReference] = []
    seen: set[CanonicalReference] = set()
    for member_name in member_names:
        inventory_entry = claim_record.member_inventory.entry_for_name(
            member_name=member_name
        )
        canonical_reference = inventory_entry.canonical_reference
        if canonical_reference is None:
            raise ParseFailureError(
                message=(
                    "Replay carrier parsing requires canonical references for "
                    f"replay-relevant member {member_name!r}"
                ),
            )
        if canonical_reference in seen:
            continue
        seen.add(canonical_reference)
        ordered.append(canonical_reference)
    return tuple(ordered)


def content_locator_from_payload(
    *,
    payload: object,
    description: str,
    claim_record: ClaimRecord,
) -> ContentLocator:
    locator = require_json_mapping(value=payload, description=description)
    kind = require_string(obj=locator, key="kind", description=description)
    media_type = require_string(obj=locator, key="mediaType", description=description)
    if kind == ContentLocatorMode.INLINE_JSON.value:
        if "content" not in locator:
            raise ParseFailureError(message=f"{description} requires field 'content'")
        return ContentLocator.inline_value(
            media_type=media_type,
            value=json_compatible_value(
                value=locator["content"],
                description=f"{description}.content",
            ),
        )
    if kind == ContentLocatorMode.PACKAGE_MEMBER.value:
        member_reference = require_string(
            obj=locator,
            key="memberReference",
            description=description,
        )
        inventory_entry = claim_record.member_inventory.entry_for_reference(
            canonical_reference=CanonicalReference(member_reference),
        )
        return ContentLocator.package_member(
            media_type=media_type,
            member_name=inventory_entry.member_name,
        )
    raise ParseFailureError(
        message=f"{description} has unsupported content-locator kind {kind!r}",
    )


def require_inline_json_object(
    *,
    locator: ContentLocator,
    description: str,
) -> dict[str, JsonCompatible]:
    if (
        locator.mode is not ContentLocatorMode.INLINE_JSON
        or locator.inline_json is None
    ):
        raise InduceFailureError(
            message=f"{description} must be preserved as inline JSON for this replay procedure",
        )
    payload = locator.inline_json.to_compatible_value()
    if not isinstance(payload, dict):
        raise InduceFailureError(
            message=f"{description} inline content must be a JSON object"
        )
    content: dict[str, JsonCompatible] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            raise InduceFailureError(
                message=f"{description} inline content keys must be strings",
            )
        content[key] = value
    return content
