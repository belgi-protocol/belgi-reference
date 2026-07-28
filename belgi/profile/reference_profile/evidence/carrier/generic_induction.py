from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.evidence.carrier.fields import (
    reference_profile_optional_environment_terms,
    reference_profile_optional_equivalence_basis,
    reference_profile_optional_json_bool,
    reference_profile_optional_json_int,
    reference_profile_optional_json_int_or_bool,
    reference_profile_optional_json_number,
)
from belgi.profile.reference_profile.evidence.carrier.parameters import (
    EVIDENCE_APPROVAL_COUNT_PARAMETER,
    EVIDENCE_AUTHORITY_LEVEL_PARAMETER,
    EVIDENCE_BLOCKING_COUNT_PARAMETER,
    EVIDENCE_BOUNDARY_PARTICIPATION_PARAMETER,
    EVIDENCE_EQUIVALENCE_BASIS_PARAMETER,
    EVIDENCE_FAILURE_COUNT_PARAMETER,
    EVIDENCE_NUMERIC_VALUE_PARAMETER,
    EVIDENCE_OUTCOME_PARAMETER,
    EVIDENCE_SEVERITY_PARAMETER,
    EVIDENCE_SOURCE_CLASS_PARAMETER,
)
from belgi.profile.reference_profile.evidence.item import ReferenceProfileEvidenceItem
from belgi.profile.reference_profile.exceptions import ReferenceProfileReplayError
from belgi.substrate.io import freeze_json_compatible_value

__all__ = ["reference_profile_generic_evidence_item"]


def reference_profile_generic_evidence_item(
    *,
    item: object,
    ordinal: int,
) -> ReferenceProfileEvidenceItem:
    evidence_identifier = _evidence_induction_required_text(
        item=item,
        attribute="evidence_identifier",
        label=f"evidence-state carrier item {ordinal}",
    )
    evidence_kind_identifier = _evidence_induction_required_text(
        item=item,
        attribute="evidence_kind_identifier",
        label=f"evidence-state carrier item {ordinal}",
    )
    source_content = _evidence_induction_required_mapping(
        value=getattr(item, "source_json_content", None),
        label=f"evidence-state carrier.evidenceItems.{evidence_identifier}.source",
    )
    description = f"evidence-state carrier.evidenceItems.{evidence_identifier}.source"
    return ReferenceProfileEvidenceItem(
        identifier=evidence_identifier,
        kind=evidence_kind_identifier,
        subject=freeze_json_compatible_value(source_content),
        source_class=_evidence_induction_optional_string_parameter(
            item=item,
            parameter_identifier=EVIDENCE_SOURCE_CLASS_PARAMETER,
            fallback=_evidence_induction_optional_source_string(
                source_content=source_content,
                key="source_class",
                description=description,
            ),
            description=description,
        ),
        boundary_participation=_evidence_induction_optional_string_parameter(
            item=item,
            parameter_identifier=EVIDENCE_BOUNDARY_PARTICIPATION_PARAMETER,
            fallback=_evidence_induction_optional_source_string(
                source_content=source_content,
                key="boundary_participation",
                description=description,
            ),
            description=description,
        ),
        authority_level=_evidence_induction_optional_string_parameter(
            item=item,
            parameter_identifier=EVIDENCE_AUTHORITY_LEVEL_PARAMETER,
            fallback=_evidence_induction_optional_source_string(
                source_content=source_content,
                key="authority_level",
                description=description,
            ),
            description=description,
        ),
        outcome=_evidence_induction_optional_string_parameter(
            item=item,
            parameter_identifier=EVIDENCE_OUTCOME_PARAMETER,
            fallback=_evidence_induction_optional_outcome(
                source_content=source_content,
                description=description,
            ),
            description=description,
        ),
        numeric_value=_evidence_induction_optional_number_parameter(
            item=item,
            parameter_identifier=EVIDENCE_NUMERIC_VALUE_PARAMETER,
            fallback=_evidence_induction_optional_numeric_value(
                source_content=source_content,
                description=description,
            ),
            description=description,
        ),
        severity=_evidence_induction_optional_string_parameter(
            item=item,
            parameter_identifier=EVIDENCE_SEVERITY_PARAMETER,
            fallback=_evidence_induction_optional_source_string(
                source_content=source_content,
                key="severity",
                description=description,
            ),
            description=description,
        ),
        failure_count=_evidence_induction_optional_int_parameter(
            item=item,
            parameter_identifier=EVIDENCE_FAILURE_COUNT_PARAMETER,
            fallback=_evidence_induction_optional_failure_count(
                source_content=source_content,
                description=description,
            ),
            description=description,
        ),
        approval_count=_evidence_induction_optional_int_parameter(
            item=item,
            parameter_identifier=EVIDENCE_APPROVAL_COUNT_PARAMETER,
            fallback=_evidence_induction_optional_approval_count(
                source_content=source_content,
                description=description,
            ),
            description=description,
        ),
        blocking_count=_evidence_induction_optional_int_parameter(
            item=item,
            parameter_identifier=EVIDENCE_BLOCKING_COUNT_PARAMETER,
            fallback=_evidence_induction_optional_blocking_count(
                source_content=source_content,
                description=description,
            ),
            description=description,
        ),
        environment_terms=reference_profile_optional_environment_terms(
            source_content=source_content
        ),
        equivalence_basis=_evidence_induction_optional_string_parameter(
            item=item,
            parameter_identifier=EVIDENCE_EQUIVALENCE_BASIS_PARAMETER,
            fallback=reference_profile_optional_equivalence_basis(
                source_content=source_content
            ),
            description=description,
        ),
    )


def _evidence_induction_required_text(
    *,
    item: object,
    attribute: str,
    label: str,
) -> str:
    value = getattr(item, attribute, None)
    if not isinstance(value, str) or not value:
        raise ReferenceProfileReplayError(
            f"{label}.{attribute} must be a non-empty string."
        )
    return value


def _evidence_induction_required_mapping(
    *,
    value: object,
    label: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ReferenceProfileReplayError(f"{label} must be a JSON object.")
    return value


def _evidence_induction_optional_source_string(
    *,
    source_content: Mapping[str, object],
    key: str,
    description: str,
) -> str | None:
    value = source_content.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ReferenceProfileReplayError(
            f"{description}.content subject_field '{key}' must be absent or a non-empty string",
        )
    return value


def _evidence_induction_parameter_value(
    *,
    item: object,
    parameter_identifier: str,
) -> object | None:
    for parameter in getattr(item, "parameters", ()):
        if (
            str(getattr(parameter, "parameter_identifier", None))
            != parameter_identifier
        ):
            continue
        value = getattr(parameter, "value", None)
        to_compatible_value = getattr(value, "to_compatible_value", None)
        if not callable(to_compatible_value):
            raise ReferenceProfileReplayError(
                f"parameter {parameter_identifier!r} must carry a compatible value."
            )
        return to_compatible_value()
    return None


def _evidence_induction_optional_string_parameter(
    *,
    item: object,
    parameter_identifier: str,
    fallback: str | None,
    description: str,
) -> str | None:
    value = _evidence_induction_parameter_value(
        item=item,
        parameter_identifier=parameter_identifier,
    )
    if value is None:
        return fallback
    if not isinstance(value, str) or not value:
        raise ReferenceProfileReplayError(
            f"{description}.parameters {parameter_identifier!r} must be a "
            "non-empty string.",
        )
    if fallback is not None and fallback != value:
        raise ReferenceProfileReplayError(
            f"{description}.parameters {parameter_identifier!r} conflicts "
            "with source content.",
        )
    return value


def _evidence_induction_optional_number_parameter(
    *,
    item: object,
    parameter_identifier: str,
    fallback: float | None,
    description: str,
) -> float | None:
    value = _evidence_induction_parameter_value(
        item=item,
        parameter_identifier=parameter_identifier,
    )
    if value is None:
        return fallback
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ReferenceProfileReplayError(
            f"{description}.parameters {parameter_identifier!r} must be numeric.",
        )
    normalized = float(value)
    if fallback is not None and fallback != normalized:
        raise ReferenceProfileReplayError(
            f"{description}.parameters {parameter_identifier!r} conflicts "
            "with source content.",
        )
    return normalized


def _evidence_induction_optional_int_parameter(
    *,
    item: object,
    parameter_identifier: str,
    fallback: int | None,
    description: str,
) -> int | None:
    value = _evidence_induction_parameter_value(
        item=item,
        parameter_identifier=parameter_identifier,
    )
    if value is None:
        return fallback
    if not isinstance(value, int) or isinstance(value, bool):
        raise ReferenceProfileReplayError(
            f"{description}.parameters {parameter_identifier!r} must be an integer.",
        )
    if fallback is not None and fallback != value:
        raise ReferenceProfileReplayError(
            f"{description}.parameters {parameter_identifier!r} conflicts "
            "with source content.",
        )
    return value


def _evidence_induction_optional_outcome(
    *,
    source_content: Mapping[str, object],
    description: str,
) -> str | None:
    for field_name in ("passed", "clean", "success"):
        value = reference_profile_optional_json_bool(
            obj=source_content,
            key=field_name,
            description=f"{description}.content",
        )
        if value is not None:
            return "pass" if value else "fail"
    for field_name in ("outcome", "status", "state", "result"):
        value = _evidence_induction_optional_source_string(
            source_content=source_content,
            key=field_name,
            description=description,
        )
        if value is not None:
            return value
    return None


def _evidence_induction_optional_numeric_value(
    *,
    source_content: Mapping[str, object],
    description: str,
) -> float | None:
    for field_name in ("numeric_value", "value", "coverage", "score", "percentage"):
        value = reference_profile_optional_json_number(
            obj=source_content,
            key=field_name,
            description=f"{description}.content",
        )
        if value is not None:
            return value
    return None


def _evidence_induction_optional_failure_count(
    *,
    source_content: Mapping[str, object],
    description: str,
) -> int | None:
    for field_name in ("failed_cases", "failures", "failed_tests"):
        value = reference_profile_optional_json_int(
            obj=source_content,
            key=field_name,
            description=f"{description}.content",
        )
        if value is not None:
            return value
    return None


def _evidence_induction_optional_approval_count(
    *,
    source_content: Mapping[str, object],
    description: str,
) -> int | None:
    for field_name in ("approval_count", "approvals", "approver_count"):
        value = reference_profile_optional_json_int(
            obj=source_content,
            key=field_name,
            description=f"{description}.content",
        )
        if value is not None:
            return value
    return None


def _evidence_induction_optional_blocking_count(
    *,
    source_content: Mapping[str, object],
    description: str,
) -> int | None:
    blocking_count = reference_profile_optional_json_int(
        obj=source_content,
        key="blocking_count",
        description=f"{description}.content",
    )
    if blocking_count is not None:
        return blocking_count
    for field_name in ("blocking_reviews", "requested_changes"):
        value = reference_profile_optional_json_int_or_bool(
            obj=source_content,
            key=field_name,
            description=f"{description}.content",
        )
        if value is None:
            continue
        if isinstance(value, bool):
            return 1 if value else 0
        return value
    return None
