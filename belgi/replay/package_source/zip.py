"""ZIP representation loader for ReplayPackageSource."""

from __future__ import annotations

from belgi.carrier.package.representation.binding import PackageRepresentationBinding
from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.replay.package_representation.exceptions import PackageRepresentationError
from belgi.replay.package_representation.zip import project_zip_bytes

from .logical_map import LogicalMapReplayPackageSource
from .physical_attempt import (
    PhysicalReplayPackageSourceAttempt,
    physical_source_attempt_from_projection,
)

__all__ = [
    "attempt_load_zip_replay_package_source",
    "load_zip_replay_package_source",
]


def load_zip_replay_package_source(
    *,
    archive_bytes: bytes,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> LogicalMapReplayPackageSource:
    attempt = attempt_load_zip_replay_package_source(
        archive_bytes=archive_bytes,
        selected_binding=selected_binding,
        supported_binding=supported_binding,
        envelope=envelope,
    )
    if attempt.source is None:
        if attempt.representation_rejection is None:
            raise RuntimeError("Rejected ZIP projection has no typed result.")
        raise PackageRepresentationError(attempt.representation_rejection)
    return attempt.source


def attempt_load_zip_replay_package_source(
    *,
    archive_bytes: bytes,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> PhysicalReplayPackageSourceAttempt:
    result = project_zip_bytes(
        archive_bytes,
        selected_binding=selected_binding,
        supported_binding=supported_binding,
        envelope=envelope,
    )
    return physical_source_attempt_from_projection(
        projection_result=result,
        envelope=envelope,
    )
