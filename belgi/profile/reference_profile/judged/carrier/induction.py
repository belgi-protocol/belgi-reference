from __future__ import annotations

from collections.abc import Mapping

from belgi.core import AdmissionSubject, JudgedObject, ReferenceContext
from belgi.profile.reference_profile.exceptions import ReferenceProfileReplayError
from belgi.profile.reference_profile.finite_evaluator.constants import PART4_DESIGNATOR
from belgi.profile.reference_profile.finite_evaluator.exceptions import (
    FiniteJudgedLiftError,
)
from belgi.profile.reference_profile.finite_evaluator.judged import (
    induce_finite_judged_object_records,
)
from belgi.substrate.io import freeze_json_compatible_value

__all__ = [
    "reference_profile_judged_object_from_carrier_endpoints",
]


def reference_profile_judged_object_from_carrier_endpoints(
    *,
    proposal: object,
    baseline: object,
    resolved_determining_source_designators: tuple[object, ...],
) -> JudgedObject:
    proposal_content = _judged_induction_required_mapping(
        value=getattr(proposal, "content", None),
        label="judged-object carrier.proposal",
    )
    baseline_content = _judged_induction_required_mapping(
        value=getattr(baseline, "content", None),
        label="judged-object carrier.baseline",
    )
    if _exact_part4_source_is_resolved(
        designators=resolved_determining_source_designators
    ):
        try:
            return induce_finite_judged_object_records(
                proposal=proposal_content,
                baseline=baseline_content,
            )
        except FiniteJudgedLiftError as exc:
            raise ReferenceProfileReplayError(
                "Part 4 judged-object carrier induction failed."
            ) from exc
    _ = _judged_induction_required_content_text(
        content=proposal_content,
        key="identifier",
        label="judged-object carrier.proposal.content",
    )
    _ = _judged_induction_required_content_text(
        content=proposal_content,
        key="source_state",
        label="judged-object carrier.proposal.content",
    )
    _ = _judged_induction_required_content_text(
        content=baseline_content,
        key="identifier",
        label="judged-object carrier.baseline.content",
    )
    _ = _judged_induction_required_content_text(
        content=baseline_content,
        key="source_state",
        label="judged-object carrier.baseline.content",
    )
    return JudgedObject(
        admission_subject=AdmissionSubject(
            value=freeze_json_compatible_value(proposal_content),
        ),
        reference_context=ReferenceContext(
            value=freeze_json_compatible_value(baseline_content),
        ),
    )


def _exact_part4_source_is_resolved(*, designators: tuple[object, ...]) -> bool:
    expected = PART4_DESIGNATOR.stable_key
    return any(
        (
            getattr(designator, "uri", None),
            getattr(getattr(designator, "digest", None), "algorithm_id", None),
            getattr(getattr(designator, "digest", None), "digest_value", None),
        )
        == expected
        for designator in designators
    )


def _judged_induction_required_mapping(
    *,
    value: object,
    label: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ReferenceProfileReplayError(f"{label} must be a JSON object.")
    return value


def _judged_induction_required_content_text(
    *,
    content: Mapping[str, object],
    key: str,
    label: str,
) -> str:
    value = content.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReferenceProfileReplayError(
            f"{label} requires a non-empty string subject_field '{key}'"
        )
    return value
