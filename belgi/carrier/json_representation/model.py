from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from belgi.substrate.schema.model import SchemaIssue

JSONRepresentationStage = Literal[
    "utf8",
    "json-syntax",
    "json-domain",
    "schema",
    "complete",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class JSONRepresentationOutcome:
    accepted: bool
    stage: JSONRepresentationStage
    result_code: str
    value: object | None = None
    canonical_bytes: bytes | None = None
    schema_issues: tuple[SchemaIssue, ...] = ()

    def __post_init__(self) -> None:
        if self.accepted != (self.stage == "complete"):
            raise ValueError("accepted JSON outcomes must have stage complete")
        if self.canonical_bytes is not None and not self.accepted:
            raise ValueError("rejected JSON outcomes cannot carry canonical bytes")
        if self.schema_issues and self.stage != "schema":
            raise ValueError("schema issues require schema-stage rejection")


__all__ = ["JSONRepresentationOutcome", "JSONRepresentationStage"]
