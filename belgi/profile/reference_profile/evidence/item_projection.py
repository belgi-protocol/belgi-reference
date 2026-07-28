from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.config.model import AdmissionConfig
from belgi.profile.reference_profile.declarations import SourceBoundaryAssignment
from belgi.profile.reference_profile.environment import (
    require_environment_compatibility_condition,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import canonical_json_bytes, freeze_json_compatible_value

from .fields import (
    reference_profile_evidence_optional_bool,
    reference_profile_evidence_optional_int,
    reference_profile_evidence_optional_int_or_bool,
    reference_profile_evidence_optional_mapping,
    reference_profile_evidence_optional_number,
    reference_profile_evidence_optional_text,
)
from .item import ReferenceProfileEvidenceItem
from .review_record import (
    REVIEW_RECORD_FIELDS,
    REVIEW_RECORD_IDENTIFIER,
    normalize_reference_profile_review_record,
)

__all__ = [
    "reference_profile_project_evidence_item",
]


def reference_profile_project_evidence_item(
    *,
    admission_artifact: AdmissionConfig,
    subject_document: Mapping[str, object],
    evidence_kind: str,
    source_class: str,
    source_assignment: SourceBoundaryAssignment,
    label: str,
) -> ReferenceProfileEvidenceItem:
    if evidence_kind == REVIEW_RECORD_IDENTIFIER:
        expected_fields = frozenset(
            (*REVIEW_RECORD_FIELDS, "evidenceKindIdentifier", "source_class")
        )
        if set(subject_document) != expected_fields:
            raise ReferenceProfileEvidenceStateCompileError(
                semantic_slice="evidence_typing",
                detail=(
                    f"{label} review-record transport must contain exactly the "
                    "two transport metadata members and the closed six-member "
                    "ReviewRecord."
                ),
            )
        try:
            review_record = normalize_reference_profile_review_record(
                document={
                    field_name: subject_document[field_name]
                    for field_name in REVIEW_RECORD_FIELDS
                },
                label=label,
            )
        except ValueError as exc:
            raise ReferenceProfileEvidenceStateCompileError(
                semantic_slice="evidence_typing",
                detail=str(exc),
            ) from exc
        subject_bytes = canonical_json_bytes(subject_document)
        return ReferenceProfileEvidenceItem(
            identifier=(
                f"urn:belgi:evidence-observation:sha256:{sha256_bytes(subject_bytes)}"
            ),
            kind=evidence_kind,
            subject=freeze_json_compatible_value(review_record),
            source_class=source_class,
            boundary_participation=None,
            authority_level=None,
            outcome=None,
            numeric_value=None,
            severity=None,
            failure_count=None,
            approval_count=None,
            blocking_count=None,
            environment_terms=None,
            equivalence_basis=None,
        )
    environment_terms = reference_profile_evidence_optional_mapping(
        document=subject_document,
        key="environment_terms",
        semantic_slice="environment_terms",
        detail_prefix=f"{label}.environment_terms",
    )
    equivalence_basis = reference_profile_evidence_optional_text(
        document=subject_document,
        key="equivalence_basis",
        semantic_slice="environment_terms",
        detail_prefix=f"{label}.equivalence_basis",
    )
    _reference_profile_require_environment_condition_for_item(
        admission_artifact=admission_artifact,
        environment_terms=environment_terms,
        equivalence_basis=equivalence_basis,
        label=label,
    )
    subject_bytes = canonical_json_bytes(subject_document)
    return ReferenceProfileEvidenceItem(
        identifier=(
            f"urn:belgi:evidence-observation:sha256:{sha256_bytes(subject_bytes)}"
        ),
        kind=evidence_kind,
        subject=freeze_json_compatible_value(subject_document),
        source_class=source_class,
        boundary_participation=str(source_assignment.boundary_participation),
        authority_level=(
            None
            if source_assignment.authority_level is None
            else str(source_assignment.authority_level)
        ),
        outcome=_reference_profile_canonical_outcome(
            subject_document=subject_document,
            label=label,
        ),
        numeric_value=_reference_profile_canonical_numeric_value(
            subject_document=subject_document,
            label=label,
        ),
        severity=reference_profile_evidence_optional_text(
            document=subject_document,
            key="severity",
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.severity",
        ),
        failure_count=_reference_profile_canonical_failure_count(
            subject_document=subject_document,
            label=label,
        ),
        approval_count=_reference_profile_canonical_approval_count(
            subject_document=subject_document,
            label=label,
        ),
        blocking_count=_reference_profile_canonical_blocking_count(
            subject_document=subject_document,
            label=label,
        ),
        environment_terms=environment_terms,
        equivalence_basis=equivalence_basis,
    )


def _reference_profile_canonical_outcome(
    *,
    subject_document: Mapping[str, object],
    label: str,
) -> str | None:
    for field_name in ("passed", "clean", "success"):
        value = reference_profile_evidence_optional_bool(
            document=subject_document,
            key=field_name,
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.{field_name}",
        )
        if value is not None:
            return "pass" if value else "fail"
    for field_name in ("outcome", "status", "state", "result"):
        value = reference_profile_evidence_optional_text(
            document=subject_document,
            key=field_name,
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.{field_name}",
        )
        if value is not None:
            return value
    return None


def _reference_profile_canonical_numeric_value(
    *,
    subject_document: Mapping[str, object],
    label: str,
) -> float | None:
    for field_name in ("numeric_value", "value", "coverage", "score", "percentage"):
        value = reference_profile_evidence_optional_number(
            document=subject_document,
            key=field_name,
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.{field_name}",
        )
        if value is not None:
            return value
    return None


def _reference_profile_canonical_failure_count(
    *,
    subject_document: Mapping[str, object],
    label: str,
) -> int | None:
    for field_name in ("failure_count", "failed_cases", "failures", "failed_tests"):
        value = reference_profile_evidence_optional_int(
            document=subject_document,
            key=field_name,
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.{field_name}",
        )
        if value is not None:
            return value
    return None


def _reference_profile_canonical_approval_count(
    *,
    subject_document: Mapping[str, object],
    label: str,
) -> int | None:
    for field_name in ("approval_count", "approvals", "approver_count"):
        value = reference_profile_evidence_optional_int(
            document=subject_document,
            key=field_name,
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.{field_name}",
        )
        if value is not None:
            return value
    return None


def _reference_profile_canonical_blocking_count(
    *,
    subject_document: Mapping[str, object],
    label: str,
) -> int | None:
    blocking_count = reference_profile_evidence_optional_int(
        document=subject_document,
        key="blocking_count",
        semantic_slice="evidence_typing",
        detail_prefix=f"{label}.blocking_count",
    )
    if blocking_count is not None:
        return blocking_count
    for field_name in ("blocking_reviews", "requested_changes"):
        value = reference_profile_evidence_optional_int_or_bool(
            document=subject_document,
            key=field_name,
            semantic_slice="evidence_typing",
            detail_prefix=f"{label}.{field_name}",
        )
        if value is None:
            continue
        if isinstance(value, bool):
            return 1 if value else 0
        return value
    return None


def _reference_profile_require_environment_condition_for_item(
    *,
    admission_artifact: AdmissionConfig,
    environment_terms: Mapping[str, object] | None,
    equivalence_basis: str | None,
    label: str,
) -> None:
    if not environment_terms and equivalence_basis is None:
        return
    declared_condition_ids = tuple(
        declaration.condition_id
        for declaration in admission_artifact.condition_declarations
    )
    try:
        require_environment_compatibility_condition(
            declared_condition_ids=declared_condition_ids,
            environment_envelope_present=True,
            surface_label=label,
        )
    except ValueError as exc:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="environment_terms",
            detail=(
                f"{label} carries an environment envelope but the admission "
                "artifact does not declare environment compatibility."
            ),
        ) from exc
