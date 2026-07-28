from __future__ import annotations

from belgi.carrier.claim_record.model import (
    ReferencedSourceBinding,
    ReferencedSourceKind,
)
from belgi.carrier.exceptions import ClaimRecordError
from belgi.carrier.inventory import CanonicalReference
from belgi.carrier.parse_support import (
    parse_immutable_designator_object,
    require_allowed_keys,
    require_mapping_object,
    require_non_empty_text,
)

__all__ = ["parse_referenced_sources"]


def parse_referenced_sources(*, value: object) -> tuple[ReferencedSourceBinding, ...]:
    payload = require_mapping_object(
        value=value,
        label="claim record.referencedSources",
        error_type=ClaimRecordError,
    )
    sources: list[ReferencedSourceBinding] = []
    for member_reference_text, source_payload in payload.items():
        if not isinstance(member_reference_text, str):
            raise ClaimRecordError(
                "referencedSources keys must be canonical references."
            )
        label = f"claim record.referencedSources.{member_reference_text}"
        source = require_mapping_object(
            value=source_payload,
            label=label,
            error_type=ClaimRecordError,
        )
        require_allowed_keys(
            payload=source,
            label=label,
            allowed_keys=frozenset({"sourceKind", "designator"}),
            error_type=ClaimRecordError,
        )
        sources.append(
            ReferencedSourceBinding(
                source_kind=ReferencedSourceKind(
                    require_non_empty_text(
                        value=source.get("sourceKind"),
                        label=f"{label}.sourceKind",
                        error_type=ClaimRecordError,
                    )
                ),
                designator=parse_immutable_designator_object(
                    value=source.get("designator"),
                    label=f"{label}.designator",
                    error_type=ClaimRecordError,
                ),
                member_reference=CanonicalReference(member_reference_text),
            )
        )
    return tuple(sources)
