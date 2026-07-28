from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)

__all__ = [
    "ReferenceProfileEvidenceTransport",
    "ReferenceProfileEvidenceTransportFileEntry",
    "reference_profile_evidence_transport_from_document",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileEvidenceTransportFileEntry:
    materialized_path: Path
    byte_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileEvidenceTransport:
    evidence_files: tuple[ReferenceProfileEvidenceTransportFileEntry, ...]


def reference_profile_evidence_transport_from_document(
    *,
    document: Mapping[str, object],
) -> ReferenceProfileEvidenceTransport:
    allowed_fields = frozenset({"evidence_files"})
    unexpected_fields = tuple(
        sorted(
            field_name for field_name in document if field_name not in allowed_fields
        )
    )
    if unexpected_fields:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_transport",
            detail=(
                "unsupported evidence-state transport fields: "
                + ", ".join(unexpected_fields)
                + "."
            ),
        )
    raw_value = document.get("evidence_files", ())
    if not isinstance(raw_value, Sequence) or isinstance(
        raw_value,
        (str, bytes, bytearray),
    ):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail="evidence_files must be a list of file entries.",
        )
    return ReferenceProfileEvidenceTransport(
        evidence_files=tuple(
            _reference_profile_evidence_transport_file_entry(
                raw_entry=raw_entry,
                ordinal=ordinal,
            )
            for ordinal, raw_entry in enumerate(raw_value, start=1)
        )
    )


def _reference_profile_evidence_transport_file_entry(
    *,
    raw_entry: object,
    ordinal: int,
) -> ReferenceProfileEvidenceTransportFileEntry:
    if not isinstance(raw_entry, Mapping):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=f"evidence_files[{ordinal}] must be an object.",
        )
    allowed_fields = frozenset({"materialized_path", "byte_count"})
    unexpected_fields = tuple(
        sorted(
            field_name for field_name in raw_entry if field_name not in allowed_fields
        )
    )
    if unexpected_fields:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=(
                f"evidence_files[{ordinal}] has unsupported fields: "
                + ", ".join(unexpected_fields)
                + "."
            ),
        )
    materialized_path = raw_entry.get("materialized_path")
    if not isinstance(materialized_path, str):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=(f"evidence_files[{ordinal}].materialized_path must be a string."),
        )
    normalized_path = materialized_path.strip()
    if not normalized_path:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=(f"evidence_files[{ordinal}].materialized_path must not be empty."),
        )
    byte_count = raw_entry.get("byte_count")
    if (
        not isinstance(byte_count, int)
        or isinstance(byte_count, bool)
        or byte_count < 0
    ):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_observations",
            detail=(
                f"evidence_files[{ordinal}].byte_count must be a non-negative int."
            ),
        )
    return ReferenceProfileEvidenceTransportFileEntry(
        materialized_path=Path(normalized_path),
        byte_count=byte_count,
    )
