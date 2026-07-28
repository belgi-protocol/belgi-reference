"""Producer-side replay-relevant projection rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from .exceptions import InvalidProjectionSpecError, ProjectionError
from .inventory.designators import ImmutableDesignator

__all__ = [
    "ProjectionMode",
    "ProjectionResult",
    "ProjectionSpec",
    "compute_projection",
]


class ProjectionMode(str, Enum):
    """How a replay-relevant projection is produced."""

    EXACT_PRESERVED_OCTETS = "exact-preserved-octets"
    PROVIDED_PROJECTION = "provided-projection"


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectionSpec:
    """Producer-side declaration of a replay-relevant projection."""

    projection_mode: ProjectionMode
    projection_rule_identifier: str | None = None
    projection_rule_designator: ImmutableDesignator | None = None
    projected_bytes: bytes | None = None

    def __post_init__(self) -> None:
        if self.projection_mode is ProjectionMode.EXACT_PRESERVED_OCTETS:
            if (
                self.projection_rule_designator is not None
                or self.projection_rule_identifier is not None
                or self.projected_bytes is not None
            ):
                raise InvalidProjectionSpecError(
                    "Exact-octet projections shall not preserve a separate rule designator or projected bytes."
                )
            return
        if self.projection_mode is ProjectionMode.PROVIDED_PROJECTION:
            if (
                self.projection_rule_identifier is None
                or self.projection_rule_designator is None
                or self.projected_bytes is None
            ):
                raise InvalidProjectionSpecError(
                    "Provided projections require a projection rule designator and projected bytes."
                )
            _require_projection_identifier(self.projection_rule_identifier)
            return
        raise InvalidProjectionSpecError(
            f"Unsupported projection mode: {self.projection_mode!r}"
        )

    @classmethod
    def exact_preserved_octets(cls) -> ProjectionSpec:
        return cls(projection_mode=ProjectionMode.EXACT_PRESERVED_OCTETS)

    @classmethod
    def provided_projection(
        cls,
        *,
        projection_rule_identifier: str,
        projection_rule_designator: ImmutableDesignator,
        projected_bytes: bytes,
    ) -> ProjectionSpec:
        return cls(
            projection_mode=ProjectionMode.PROVIDED_PROJECTION,
            projection_rule_identifier=projection_rule_identifier,
            projection_rule_designator=projection_rule_designator,
            projected_bytes=projected_bytes,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectionResult:
    """Computed replay-relevant projection for one replay-relevant member."""

    projection_mode: ProjectionMode
    projection_rule_identifier: str | None
    projection_rule_designator: ImmutableDesignator | None
    projected_bytes: bytes


def compute_projection(
    *,
    preserved_bytes: bytes,
    projection_spec: ProjectionSpec | None,
) -> ProjectionResult:
    """Compute the replay-relevant projection for one preserved member."""

    if (
        projection_spec is None
        or projection_spec.projection_mode is ProjectionMode.EXACT_PRESERVED_OCTETS
    ):
        return ProjectionResult(
            projection_mode=ProjectionMode.EXACT_PRESERVED_OCTETS,
            projection_rule_identifier=None,
            projection_rule_designator=None,
            projected_bytes=preserved_bytes,
        )
    projection_rule_identifier = projection_spec.projection_rule_identifier
    projection_rule_designator = projection_spec.projection_rule_designator
    projected_bytes = projection_spec.projected_bytes
    if (
        projection_rule_identifier is None
        or projection_rule_designator is None
        or projected_bytes is None
    ):
        raise ProjectionError(
            "Provided projections require a projection rule designator and projected bytes."
        )
    return ProjectionResult(
        projection_mode=projection_spec.projection_mode,
        projection_rule_identifier=projection_rule_identifier,
        projection_rule_designator=projection_rule_designator,
        projected_bytes=projected_bytes,
    )


def _require_projection_identifier(value: str) -> None:
    if not value or value != value.strip():
        raise InvalidProjectionSpecError(
            "Projection-rule identifier must be exact non-empty text."
        )
    parsed = urlparse(value)
    if not parsed.scheme or parsed.fragment:
        raise InvalidProjectionSpecError(
            "Projection-rule identifier must be an absolute URI without a fragment."
        )
