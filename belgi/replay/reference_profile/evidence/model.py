"""Resolved reference-profile evidence values used by replay lifting."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ReferenceProfileEvidenceCarrierItem"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileEvidenceCarrierItem:
    evidence_identifier: str
    evidence_kind_identifier: str
    source_json_content: object | None
    source_media_type: str
    source_preserved_octets: bytes | None
    parameters: tuple[object, ...]
