"""Isolated portable-path and physical-mapping observations."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.carrier.package.representation.paths import (
    physical_path_for_logical_path,
    require_portable_logical_path,
)

__all__ = ["PathOperationResult", "map_logical_path", "validate_logical_path"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PathOperationResult:
    accepted: bool
    stage: int
    result_code: str
    physical_path: str | None = None


def validate_logical_path(
    logical_path: str,
    *,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> PathOperationResult:
    try:
        require_portable_logical_path(logical_path, envelope=envelope)
    except ValueError:
        return PathOperationResult(
            accepted=False,
            stage=4,
            result_code="invalid-entry-name",
        )
    return PathOperationResult(accepted=True, stage=8, result_code="complete")


def map_logical_path(
    logical_path: str,
    *,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> PathOperationResult:
    try:
        physical_path = physical_path_for_logical_path(
            logical_path,
            envelope=envelope,
        )
    except ValueError:
        return PathOperationResult(
            accepted=False,
            stage=4,
            result_code="invalid-entry-name",
        )
    return PathOperationResult(
        accepted=True,
        stage=8,
        result_code="complete",
        physical_path=physical_path,
    )
