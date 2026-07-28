"""Independent finite judged-object induction."""

from __future__ import annotations

from collections.abc import Mapping

from belgi.core import AdmissionSubject, JudgedObject, ReferenceContext
from belgi.substrate.io import freeze_json_compatible_value

from .exceptions import FiniteJudgedLiftError

_PROPOSAL_FIELDS = frozenset({"proposalIdentifier", "proposedSourceStateIdentifier"})
_BASELINE_FIELDS = frozenset(
    {"baselineRevisionIdentifier", "baselineSourceStateIdentifier"}
)


def induce_finite_judged_object_document(
    *, document: Mapping[str, object]
) -> JudgedObject:
    """Induce J from an already decoded finite judged carrier."""

    if set(document) != {"kind", "proposal", "baseline"}:
        raise FiniteJudgedLiftError("finite judged carrier must be closed.")
    if document.get("kind") != "judged-object-carrier":
        raise FiniteJudgedLiftError("finite judged carrier kind is unsupported.")
    proposal = _endpoint_content(document.get("proposal"), label="proposal")
    baseline = _endpoint_content(document.get("baseline"), label="baseline")
    return induce_finite_judged_object_records(
        proposal=proposal,
        baseline=baseline,
    )


def induce_finite_judged_object_records(
    *, proposal: object, baseline: object
) -> JudgedObject:
    """Induce J from the two closed finite logical records."""

    proposal_record, baseline_record = _finite_judged_records(
        proposal=proposal,
        baseline=baseline,
    )
    return JudgedObject(
        admission_subject=AdmissionSubject(
            value=freeze_json_compatible_value(proposal_record)
        ),
        reference_context=ReferenceContext(
            value=freeze_json_compatible_value(baseline_record)
        ),
    )


def finite_judged_source_state_identifiers(
    *, proposal: object, baseline: object
) -> tuple[str, str]:
    """Return the exact finite source-state recovery keys after record validation."""

    proposal_record, baseline_record = _finite_judged_records(
        proposal=proposal,
        baseline=baseline,
    )
    return (
        proposal_record["proposedSourceStateIdentifier"],
        baseline_record["baselineSourceStateIdentifier"],
    )


def _finite_judged_records(
    *, proposal: object, baseline: object
) -> tuple[dict[str, str], dict[str, str]]:
    return (
        _closed_record(
            proposal,
            fields=_PROPOSAL_FIELDS,
            label="ProposalRecord",
        ),
        _closed_record(
            baseline,
            fields=_BASELINE_FIELDS,
            label="BaselineRecord",
        ),
    )


def _endpoint_content(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise FiniteJudgedLiftError(f"finite judged {label} must be an object.")
    if set(value) != {"kind", "mediaType", "content"}:
        raise FiniteJudgedLiftError(f"finite judged {label} locator must be closed.")
    if (
        value.get("kind") != "inline-json"
        or value.get("mediaType") != "application/json"
    ):
        raise FiniteJudgedLiftError(
            f"finite judged {label} must be resolved inline JSON."
        )
    content = value.get("content")
    if not isinstance(content, Mapping):
        raise FiniteJudgedLiftError(f"finite judged {label} content must be an object.")
    return content


def _closed_record(
    value: object,
    *,
    fields: frozenset[str],
    label: str,
) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise FiniteJudgedLiftError(f"{label} must contain exactly its closed fields.")
    record: dict[str, str] = {}
    for field in sorted(fields):
        member = value.get(field)
        if not isinstance(member, str) or not member:
            raise FiniteJudgedLiftError(
                f"{label}.{field} must be a non-empty exact string."
            )
        record[field] = member
    return record
