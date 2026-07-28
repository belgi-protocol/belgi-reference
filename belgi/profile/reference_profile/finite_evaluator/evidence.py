"""Independent finite evidence-state induction."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from belgi.core import EvidenceState
from belgi.profile.reference_profile.evidence.review_record import (
    normalize_reference_profile_review_record,
)
from belgi.profile.reference_profile.identifiers.evidence_kinds import REVIEW_RECORD
from belgi.profile.reference_profile.identifiers.parameters import (
    EVIDENCE_SOURCE_CLASS_PARAMETER,
)
from belgi.substrate.io import freeze_json_compatible_value

from .constants import (
    RECOGNIZED_EVIDENCE_KINDS,
    RECOGNIZED_SOURCE_CLASSES,
)
from .exceptions import FiniteEvidenceLiftError
from .model import (
    FiniteEvidenceItem,
    FiniteOpaqueEvidenceSubject,
    FiniteReviewRecord,
)


def induce_finite_evidence_state_document(
    *, document: Mapping[str, object]
) -> EvidenceState:
    """Induce E from an already decoded finite evidence carrier."""

    if set(document) != {"kind", "evidenceItems"}:
        raise FiniteEvidenceLiftError("finite evidence carrier must be closed.")
    if document.get("kind") != "evidence-state-carrier":
        raise FiniteEvidenceLiftError("finite evidence carrier kind is unsupported.")
    items = document.get("evidenceItems")
    if not isinstance(items, Mapping):
        raise FiniteEvidenceLiftError("finite evidenceItems must be an object.")
    return EvidenceState(
        items=tuple(
            _induce_item(identifier=identifier, value=value)
            for identifier, value in sorted(items.items())
        )
    )


def induce_finite_evidence_state_carrier_items(
    *, carrier_items: Iterable[object]
) -> EvidenceState:
    """Induce E from parsed production carrier items without weakening bytes."""

    return EvidenceState(
        items=tuple(
            _induce_carrier_item(item=item, ordinal=ordinal)
            for ordinal, item in enumerate(carrier_items, start=1)
        )
    )


def _induce_carrier_item(*, item: object, ordinal: int) -> FiniteEvidenceItem:
    identifier = getattr(item, "evidence_identifier", None)
    kind = getattr(item, "evidence_kind_identifier", None)
    if not isinstance(identifier, str) or not identifier:
        raise FiniteEvidenceLiftError(
            f"parsed finite evidence item {ordinal} has an invalid identifier."
        )
    if not isinstance(kind, str) or kind not in RECOGNIZED_EVIDENCE_KINDS:
        raise FiniteEvidenceLiftError(
            f"evidence item {identifier!r} has no exact owning evidence kind."
        )
    preserved_octets = getattr(item, "source_preserved_octets", None)
    if preserved_octets is not None and kind != REVIEW_RECORD:
        media_type = getattr(item, "source_media_type", None)
        if not isinstance(media_type, str) or not media_type:
            raise FiniteEvidenceLiftError(
                f"evidence source {identifier!r} media type is invalid."
            )
        if not isinstance(preserved_octets, bytes):
            raise FiniteEvidenceLiftError(
                f"evidence source {identifier!r} preserved octets are invalid."
            )
        return FiniteEvidenceItem(
            identifier=identifier,
            kind=kind,
            subject=FiniteOpaqueEvidenceSubject(
                media_type=media_type,
                preserved_octets=preserved_octets,
            ),
            source_class=None,
            review=None,
        )
    content = getattr(item, "source_json_content", None)
    if not isinstance(content, Mapping):
        raise FiniteEvidenceLiftError(
            f"evidence source {identifier!r} content must be an object."
        )
    if kind != REVIEW_RECORD:
        return FiniteEvidenceItem(
            identifier=identifier,
            kind=kind,
            subject=freeze_json_compatible_value(content),
            source_class=None,
            review=None,
        )
    source_class = _review_source_class(
        _carrier_parameter_documents(item=item),
        identifier=identifier,
    )
    return FiniteEvidenceItem(
        identifier=identifier,
        kind=kind,
        subject=freeze_json_compatible_value(content),
        source_class=source_class,
        review=_review_record(content, identifier=identifier),
    )


def _carrier_parameter_documents(*, item: object) -> list[dict[str, object]]:
    parameters: list[dict[str, object]] = []
    for parameter in getattr(item, "parameters", ()):
        value = getattr(parameter, "value", None)
        project = getattr(value, "to_compatible_value", None)
        if not callable(project):
            raise FiniteEvidenceLiftError(
                "parsed finite evidence parameter value is invalid."
            )
        parameters.append(
            {
                "parameterIdentifier": str(
                    getattr(parameter, "parameter_identifier", "")
                ),
                "value": project(),
            }
        )
    return parameters


def _induce_item(*, identifier: object, value: object) -> FiniteEvidenceItem:
    if not isinstance(identifier, str) or not identifier:
        raise FiniteEvidenceLiftError("evidence identifier must be non-empty text.")
    if not isinstance(value, Mapping):
        raise FiniteEvidenceLiftError(
            f"evidence item {identifier!r} must be an object."
        )
    if set(value) != {"evidenceKindIdentifier", "source", "parameters"}:
        raise FiniteEvidenceLiftError(f"evidence item {identifier!r} must be closed.")
    kind = value.get("evidenceKindIdentifier")
    if not isinstance(kind, str) or kind not in RECOGNIZED_EVIDENCE_KINDS:
        raise FiniteEvidenceLiftError(
            f"evidence item {identifier!r} has no exact owning evidence kind."
        )
    content = _source_content(value.get("source"), identifier=identifier)
    if kind != REVIEW_RECORD:
        return FiniteEvidenceItem(
            identifier=identifier,
            kind=kind,
            subject=freeze_json_compatible_value(content),
            source_class=None,
            review=None,
        )
    source_class = _review_source_class(
        value.get("parameters"),
        identifier=identifier,
    )
    return FiniteEvidenceItem(
        identifier=identifier,
        kind=kind,
        subject=freeze_json_compatible_value(content),
        source_class=source_class,
        review=_review_record(content, identifier=identifier),
    )


def _source_content(value: object, *, identifier: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise FiniteEvidenceLiftError(
            f"evidence source {identifier!r} must be an object."
        )
    if set(value) != {"kind", "mediaType", "content"}:
        raise FiniteEvidenceLiftError(f"evidence source {identifier!r} must be closed.")
    if (
        value.get("kind") != "inline-json"
        or value.get("mediaType") != "application/json"
    ):
        raise FiniteEvidenceLiftError(
            f"evidence source {identifier!r} must be resolved inline JSON."
        )
    content = value.get("content")
    if not isinstance(content, Mapping):
        raise FiniteEvidenceLiftError(
            f"evidence source {identifier!r} content must be an object."
        )
    return content


def _review_source_class(value: object, *, identifier: str) -> str:
    if not isinstance(value, list) or len(value) != 1:
        raise FiniteEvidenceLiftError(
            f"review item {identifier!r} requires exactly one declaration parameter."
        )
    parameter = value[0]
    if not isinstance(parameter, Mapping) or set(parameter) != {
        "parameterIdentifier",
        "value",
    }:
        raise FiniteEvidenceLiftError(
            f"review item {identifier!r} parameter must be closed."
        )
    if parameter.get("parameterIdentifier") != EVIDENCE_SOURCE_CLASS_PARAMETER:
        raise FiniteEvidenceLiftError(
            f"review item {identifier!r} source-class parameter is invalid."
        )
    source_class = parameter.get("value")
    if (
        not isinstance(source_class, str)
        or source_class not in RECOGNIZED_SOURCE_CLASSES
    ):
        raise FiniteEvidenceLiftError(
            f"review item {identifier!r} source class is unsupported."
        )
    return source_class


def _review_record(
    value: Mapping[str, object], *, identifier: str
) -> FiniteReviewRecord:
    try:
        fields = normalize_reference_profile_review_record(
            document=value,
            label=f"review item {identifier!r}",
        )
    except ValueError as exc:
        raise FiniteEvidenceLiftError(
            "Part 4 review-record validation failed."
        ) from exc
    return FiniteReviewRecord(
        review_identifier=fields["reviewIdentifier"],
        proposal_identifier=fields["proposalIdentifier"],
        proposed_source_state_identifier=fields["proposedSourceStateIdentifier"],
        baseline_revision_identifier=fields["baselineRevisionIdentifier"],
        baseline_source_state_identifier=fields["baselineSourceStateIdentifier"],
        decision=fields["decision"],
    )
