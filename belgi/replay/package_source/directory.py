"""Directory representation loader for ReplayPackageSource."""

from __future__ import annotations

from pathlib import Path

from belgi.carrier.package.representation.binding import PackageRepresentationBinding
from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.replay.package_representation.directory import project_directory_path
from belgi.replay.package_representation.exceptions import PackageRepresentationError

from .logical_map import LogicalMapReplayPackageSource
from .physical_attempt import (
    PhysicalReplayPackageSourceAttempt,
    physical_source_attempt_from_projection,
)

__all__ = [
    "attempt_load_directory_replay_package_source",
    "load_directory_replay_package_source",
]


def load_directory_replay_package_source(
    *,
    path: Path,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> LogicalMapReplayPackageSource:
    attempt = attempt_load_directory_replay_package_source(
        path=path,
        selected_binding=selected_binding,
        supported_binding=supported_binding,
        envelope=envelope,
    )
    if attempt.source is None:
        if attempt.representation_rejection is None:
            raise RuntimeError("Rejected directory projection has no typed result.")
        raise PackageRepresentationError(attempt.representation_rejection)
    return attempt.source


def attempt_load_directory_replay_package_source(
    *,
    path: Path,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> PhysicalReplayPackageSourceAttempt:
    result = project_directory_path(
        path,
        selected_binding=selected_binding,
        supported_binding=supported_binding,
        envelope=envelope,
    )
    return physical_source_attempt_from_projection(
        projection_result=result,
        envelope=envelope,
    )
