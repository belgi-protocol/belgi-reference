"""Authenticated physical directory/ZIP package selection."""

from __future__ import annotations

from pathlib import Path

from belgi.carrier.package.representation.contract import BASELINE_ENVELOPE
from belgi.profile.companions.json_representation.selection import (
    DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER,
    ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER,
)
from belgi.replay.package_representation.installed import (
    installed_package_representation_binding,
)
from belgi.replay.package_representation.model import rejected_result
from belgi.replay.package_source.directory import (
    attempt_load_directory_replay_package_source,
)
from belgi.replay.package_source.physical_attempt import (
    PhysicalReplayPackageSourceAttempt,
    physical_source_attempt_from_projection,
)
from belgi.replay.package_source.zip import attempt_load_zip_replay_package_source
from belgi.substrate.io.posix.metadata import is_directory, is_regular_file
from belgi.substrate.io.rooted_snapshot.api import open_binary_file_snapshot

from .exceptions import UnsupportedPackagePathKindError

__all__ = [
    "load_physical_replay_package_attempt",
]


def load_physical_replay_package_attempt(
    *,
    path: Path,
) -> PhysicalReplayPackageSourceAttempt:
    path_status = path.lstat()
    if is_directory(path_status):
        physical_directory = path.resolve(strict=True)
        binding = installed_package_representation_binding(
            procedure_identifier=(DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER)
        )
        return attempt_load_directory_replay_package_source(
            path=physical_directory,
            selected_binding=binding,
            supported_binding=binding,
        )
    if not is_regular_file(path_status):
        raise UnsupportedPackagePathKindError(
            f"replay package path has unsupported filesystem kind: {path}"
        )

    archive_bytes = _read_bounded_zip_snapshot(path=path)
    if archive_bytes is None:
        return physical_source_attempt_from_projection(
            projection_result=rejected_result(
                stage=1,
                result_code="outer-size-exceeded",
            )
        )
    binding = installed_package_representation_binding(
        procedure_identifier=ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER
    )
    return attempt_load_zip_replay_package_source(
        archive_bytes=archive_bytes,
        selected_binding=binding,
        supported_binding=binding,
    )


def _read_bounded_zip_snapshot(*, path: Path) -> bytes | None:
    maximum_bytes = BASELINE_ENVELOPE.outer_zip_bytes
    snapshot_root = path.parent.resolve(strict=True)
    snapshot_path = snapshot_root / path.name
    with open_binary_file_snapshot(snapshot_path, root=snapshot_root) as (stream, _):
        archive_bytes = stream.read(maximum_bytes + 1)
    if len(archive_bytes) > maximum_bytes:
        return None
    return archive_bytes
