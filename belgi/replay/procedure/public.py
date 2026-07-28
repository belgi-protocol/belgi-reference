"""Thin installed composition over the authoritative Part 2 replay procedure."""

from __future__ import annotations

from pathlib import Path

from belgi.replay.package_source.path import load_physical_replay_package_attempt
from belgi.replay.procedure.physical import (
    PhysicalReplayObservation,
    observe_physical_replay,
)
from belgi.replay.reference_profile.procedure import (
    recover_reference_profile_execution,
)

__all__ = ["run_public_replay"]


def run_public_replay(*, package_path: Path) -> PhysicalReplayObservation:
    attempt = load_physical_replay_package_attempt(path=package_path)
    return observe_physical_replay(
        attempt=attempt,
        recover=recover_reference_profile_execution,
    )
