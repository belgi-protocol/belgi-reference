from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.config.model import AdmissionConfig
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)
from belgi.profile.reference_profile.identifiers.evidence_kinds import (
    ALL_EVIDENCE_KINDS,
)
from belgi.substrate.io import load_json_object

from .fields import reference_profile_evidence_required_text
from .item import ReferenceProfileEvidenceItem
from .item_projection import reference_profile_project_evidence_item
from .source_regime import (
    reference_profile_evidence_source_assignment,
)
from .transport import (
    ReferenceProfileEvidenceTransport,
    ReferenceProfileEvidenceTransportFileEntry,
)

__all__ = [
    "reference_profile_evidence_items_from_transport",
]


def reference_profile_evidence_items_from_transport(
    *,
    admission_artifact: AdmissionConfig,
    transport: ReferenceProfileEvidenceTransport,
) -> tuple[ReferenceProfileEvidenceItem, ...]:
    return tuple(
        _reference_profile_evidence_item_from_file(
            admission_artifact=admission_artifact,
            transport_file=transport_file,
            ordinal=ordinal,
        )
        for ordinal, transport_file in enumerate(transport.evidence_files, start=1)
    )


def _reference_profile_evidence_item_from_file(
    *,
    admission_artifact: AdmissionConfig,
    transport_file: ReferenceProfileEvidenceTransportFileEntry,
    ordinal: int,
) -> ReferenceProfileEvidenceItem:
    label = f"evidence_files[{ordinal}]"
    _reference_profile_validate_evidence_file_observation(
        transport_file=transport_file,
        label=label,
    )
    subject_document = _reference_profile_evidence_subject_document(
        transport_file=transport_file,
        label=label,
    )
    evidence_kind = _reference_profile_evidence_kind_identifier(
        admission_artifact=admission_artifact,
        subject_document=subject_document,
        label=label,
    )
    source_class = _reference_profile_evidence_source_class_identifier(
        subject_document=subject_document,
        label=label,
    )
    source_assignment = reference_profile_evidence_source_assignment(
        admission_artifact=admission_artifact,
        source_class=source_class,
        label=label,
    )
    return reference_profile_project_evidence_item(
        admission_artifact=admission_artifact,
        subject_document=subject_document,
        evidence_kind=evidence_kind,
        source_class=source_class,
        source_assignment=source_assignment,
        label=label,
    )


def _reference_profile_validate_evidence_file_observation(
    *,
    transport_file: ReferenceProfileEvidenceTransportFileEntry,
    label: str,
) -> None:
    materialized_path = transport_file.materialized_path
    if not materialized_path.is_file():
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=f"{label}.materialized_path must point to an existing file.",
        )
    actual_byte_count = materialized_path.stat().st_size
    if actual_byte_count != transport_file.byte_count:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=(
                f"{label}.byte_count does not match the observed file size: "
                f"expected {transport_file.byte_count}, saw {actual_byte_count}."
            ),
        )


def _reference_profile_evidence_subject_document(
    *,
    transport_file: ReferenceProfileEvidenceTransportFileEntry,
    label: str,
) -> dict[str, object]:
    try:
        return load_json_object(
            transport_file.materialized_path,
            label=f"{label} {transport_file.materialized_path}",
        )
    except ValueError as exc:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=(
                f"{label}.materialized_path must contain a UTF-8 JSON object "
                "before evidence typing can run."
            ),
        ) from exc


def _reference_profile_evidence_kind_identifier(
    *,
    admission_artifact: AdmissionConfig,
    subject_document: Mapping[str, object],
    label: str,
) -> str:
    evidence_kind = reference_profile_evidence_required_text(
        document=subject_document,
        key="evidenceKindIdentifier",
        semantic_slice="evidence_typing",
        detail_prefix=f"{label}.evidenceKindIdentifier",
    )
    if evidence_kind not in _reference_profile_declared_evidence_kind_identifiers(
        admission_artifact=admission_artifact,
    ):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_typing",
            detail=(
                f"{label}.evidenceKindIdentifier must be declared by the selected "
                f"profile or companion surface, got {evidence_kind!r}."
            ),
        )
    return evidence_kind


def _reference_profile_declared_evidence_kind_identifiers(
    *,
    admission_artifact: AdmissionConfig,
) -> frozenset[str]:
    identifiers = {str(kind) for kind in ALL_EVIDENCE_KINDS}
    for declaration in admission_artifact.condition_declarations:
        for binding in getattr(declaration, "required_bindings", ()):
            evidence_kind = getattr(binding, "evidence_kind", None)
            if evidence_kind is not None:
                identifiers.add(str(evidence_kind))
    return frozenset(identifiers)


def _reference_profile_evidence_source_class_identifier(
    *,
    subject_document: Mapping[str, object],
    label: str,
) -> str:
    source_class = reference_profile_evidence_required_text(
        document=subject_document,
        key="source_class",
        semantic_slice="source_regime",
        detail_prefix=f"{label}.source_class",
    )
    return source_class
