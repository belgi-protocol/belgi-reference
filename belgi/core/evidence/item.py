from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from belgi.core.validation import require_identifier

EvidenceItemId = NewType("EvidenceItemId", str)
EvidenceKindId = NewType("EvidenceKindId", str)

__all__ = ["EvidenceItem", "EvidenceItemId", "EvidenceKindId"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceItem:
    item_id: EvidenceItemId | None = None
    kind_id: EvidenceKindId | None = None
    subject: object

    def __post_init__(self) -> None:
        if self.item_id is not None:
            require_identifier(
                owner="EvidenceItem",
                name="item_id",
                value=self.item_id,
            )
        if self.kind_id is not None:
            require_identifier(
                owner="EvidenceItem",
                name="kind_id",
                value=self.kind_id,
            )
