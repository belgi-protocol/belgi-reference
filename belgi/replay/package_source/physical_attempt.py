"""Stable physical-source load attempts across representation Stage 6."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.carrier.package.representation.paths import (
    physical_path_for_logical_path,
)
from belgi.replay.package_representation.model import RepresentationResult

from .logical_map import (
    LogicalMapReplayPackageSource,
    claim_record_projection_rejection,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PhysicalReplayPackageSourceAttempt:
    representation_rejection: RepresentationResult | None
    source: LogicalMapReplayPackageSource | None
    _stage5_snapshot: LogicalMapReplayPackageSource | None

    def step1_snapshot(self) -> LogicalMapReplayPackageSource | None:
        """Expose rejected Stage-6 bytes only to the integrated Step-1 observer."""

        return self._stage5_snapshot


def physical_source_attempt_from_projection(
    *,
    projection_result: RepresentationResult,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> PhysicalReplayPackageSourceAttempt:
    members = projection_result.logical_map
    if not projection_result.accepted or members is None:
        return PhysicalReplayPackageSourceAttempt(
            representation_rejection=projection_result,
            source=None,
            _stage5_snapshot=None,
        )
    snapshot = LogicalMapReplayPackageSource(
        members=members,
        physical_paths=tuple(
            physical_path_for_logical_path(
                member.logical_path,
                envelope=envelope,
            )
            for member in members
        ),
        resource_envelope=envelope,
    )
    stage6_rejection = claim_record_projection_rejection(
        members=members,
        envelope=envelope,
    )
    if stage6_rejection is not None:
        return PhysicalReplayPackageSourceAttempt(
            representation_rejection=stage6_rejection,
            source=None,
            _stage5_snapshot=snapshot,
        )
    return PhysicalReplayPackageSourceAttempt(
        representation_rejection=None,
        source=snapshot,
        _stage5_snapshot=None,
    )


__all__ = [
    "PhysicalReplayPackageSourceAttempt",
    "physical_source_attempt_from_projection",
]
