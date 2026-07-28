from __future__ import annotations

import subprocess
from pathlib import Path
from types import ModuleType

import pytest


def _git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _committed_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "repository"
    _git(tmp_path, "init", str(repository))
    _git(repository, "config", "user.name", "BELGI Test")
    _git(repository, "config", "user.email", "test@belgi.invalid")
    (repository / "source.txt").write_bytes(b"admitted source\n")
    _git(repository, "add", "source.txt")
    _git(repository, "commit", "-m", "initial")
    return repository, _git(repository, "rev-parse", "HEAD")


def test_materialized_source_is_the_exact_committed_tree(
    tmp_path: Path,
    archives_module: ModuleType,
) -> None:
    repository, commit = _committed_repository(tmp_path)
    archive_path = tmp_path / "source.tar"
    destination = tmp_path / "tag-source"

    archives_module.materialize_source_archive(
        repository=repository,
        commit=commit,
        archive_path=archive_path,
        destination=destination,
    )

    assert archive_path.is_file()
    assert (destination / "source.txt").read_bytes() == b"admitted source\n"


def test_materialized_source_rejects_checkout_byte_drift(
    tmp_path: Path,
    archives_module: ModuleType,
) -> None:
    repository, commit = _committed_repository(tmp_path)
    (repository / "source.txt").write_bytes(b"changed checkout\n")

    with pytest.raises(
        archives_module.ReleaseArtifactError,
        match="tag archive byte mismatch",
    ):
        archives_module.materialize_source_archive(
            repository=repository,
            commit=commit,
            archive_path=tmp_path / "source.tar",
            destination=tmp_path / "tag-source",
        )


def test_materialized_source_rejects_revision_option_shape(
    tmp_path: Path,
    archives_module: ModuleType,
) -> None:
    repository, _ = _committed_repository(tmp_path)

    with pytest.raises(
        archives_module.ReleaseArtifactError,
        match="source commit must be",
    ):
        archives_module.materialize_source_archive(
            repository=repository,
            commit="--output=unexpected",
            archive_path=tmp_path / "source.tar",
            destination=tmp_path / "tag-source",
        )
