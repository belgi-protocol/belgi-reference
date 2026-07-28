from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier.exceptions import JudgedCarrierError
from belgi.carrier.inventory import ContentLocator, JsonCompatible

from .carrier import JudgedObjectCarrier

__all__ = ["judged_object_carrier_from_projection"]


def judged_object_carrier_from_projection(
    *,
    carrier_projection: object,
) -> JudgedObjectCarrier:
    return JudgedObjectCarrier(
        proposal=_content_locator_from_projection_endpoint(
            endpoint=getattr(carrier_projection, "proposal", None),
            label="carrier_projection.proposal",
        ),
        baseline=_content_locator_from_projection_endpoint(
            endpoint=getattr(carrier_projection, "baseline", None),
            label="carrier_projection.baseline",
        ),
    )


def _content_locator_from_projection_endpoint(
    *,
    endpoint: object,
    label: str,
) -> ContentLocator:
    if endpoint is None:
        raise JudgedCarrierError(f"{label} is required.")
    media_type = getattr(endpoint, "media_type", None)
    if not isinstance(media_type, str) or not media_type:
        raise JudgedCarrierError(f"{label}.media_type must be a non-empty string.")
    content = getattr(endpoint, "content", None)
    return ContentLocator.inline_value(
        media_type=media_type,
        value=_require_judged_projection_json(
            value=content,
            label=f"{label}.content",
        ),
    )


def _require_judged_projection_json(
    *,
    value: object,
    label: str,
) -> JsonCompatible:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [
            _require_judged_projection_json(value=item, label=f"{label}[]")
            for item in value
        ]
    if isinstance(value, Mapping):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise JudgedCarrierError(f"{label} must use string object keys.")
            converted[key] = _require_judged_projection_json(
                value=item,
                label=f"{label}.{key}",
            )
        return converted
    raise JudgedCarrierError(f"{label} must contain only JSON-compatible values.")
