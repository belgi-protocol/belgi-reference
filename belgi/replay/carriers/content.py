from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier import (
    ClaimRecord,
    ContentLocator,
    ContentLocatorMode,
    JsonCompatible,
)
from belgi.replay.lifting.exceptions import ParseFailureError, ResolveFailureError
from belgi.replay.lifting.model import ResolvedDependencies
from belgi.replay.lifting.parsing import load_member_json_object

__all__ = [
    "resolved_content_locator_json_object",
]


def _require_json_object(
    *,
    value: JsonCompatible,
    description: str,
) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ResolveFailureError(message=f"{description} must be a JSON object.")
    return value


def resolved_content_locator_json_object(
    *,
    locator: ContentLocator,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
    description: str,
) -> Mapping[str, object]:
    if locator.mode is ContentLocatorMode.INLINE_JSON:
        if locator.inline_json is None:
            raise ResolveFailureError(
                message=f"{description} inline locator has no inline content."
            )
        return _require_json_object(
            value=locator.inline_json.to_compatible_value(),
            description=description,
        )
    if locator.mode is not ContentLocatorMode.PACKAGE_MEMBER:
        raise ResolveFailureError(
            message=f"{description} has unsupported locator mode {locator.mode!r}."
        )
    if locator.member_name is None:
        raise ResolveFailureError(
            message=f"{description} package-member locator has no member name."
        )
    inventory_entry = claim_record.member_inventory.entry_for_name(
        member_name=locator.member_name
    )
    canonical_reference = inventory_entry.canonical_reference
    if canonical_reference is None:
        raise ResolveFailureError(
            message=f"{description} package-member locator has no canonical reference."
        )
    dependency = dependencies.member_for_reference(
        canonical_reference=canonical_reference
    )
    if dependency is None:
        raise ResolveFailureError(
            message=f"{description} package-member dependency was not resolved.",
            related_reference=canonical_reference,
        )
    try:
        return load_member_json_object(
            octets=dependency.preserved_bytes,
            description=description,
        )
    except ParseFailureError as exc:
        raise ResolveFailureError(
            message=str(exc),
            related_reference=canonical_reference,
        ) from exc
