from __future__ import annotations

import subprocess
from pathlib import Path
from types import ModuleType

import pytest

_TAG = "v0.1.0a0"


def _git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _remote_with_annotated_tag(tmp_path: Path) -> tuple[Path, Path, str, str]:
    remote = tmp_path / "remote.git"
    source = tmp_path / "source"
    _git(tmp_path, "init", "--bare", str(remote))
    _git(tmp_path, "init", str(source))
    _git(source, "config", "user.name", "BELGI Test")
    _git(source, "config", "user.email", "test@belgi.invalid")
    _git(source, "commit", "--allow-empty", "-m", "initial")
    _git(source, "tag", "-a", _TAG, "-m", "release")
    _git(source, "remote", "add", "origin", str(remote))
    _git(source, "push", "origin", "HEAD:main", f"refs/tags/{_TAG}")
    commit = _git(source, "rev-parse", "HEAD")
    tag_object = _git(source, "rev-parse", f"refs/tags/{_TAG}^{{tag}}")
    return remote, source, tag_object, commit


def test_remote_tag_rebind_accepts_the_exact_annotated_tag(
    tmp_path: Path,
    release_tag_module: ModuleType,
) -> None:
    remote, _, tag_object, commit = _remote_with_annotated_tag(tmp_path)

    release_tag_module.verify_remote_tag(
        repository=str(remote),
        tag=_TAG,
        tag_object=tag_object,
        commit=commit,
    )


def test_remote_tag_rebind_rejects_tag_movement(
    tmp_path: Path,
    release_tag_module: ModuleType,
) -> None:
    remote, source, tag_object, commit = _remote_with_annotated_tag(tmp_path)
    _git(source, "commit", "--allow-empty", "-m", "moved")
    _git(source, "tag", "-d", _TAG)
    _git(source, "tag", "-a", _TAG, "-m", "moved release")
    _git(source, "push", "--force", "origin", f"refs/tags/{_TAG}")

    with pytest.raises(
        release_tag_module.RemoteTagError,
        match="moved or disappeared",
    ):
        release_tag_module.verify_remote_tag(
            repository=str(remote),
            tag=_TAG,
            tag_object=tag_object,
            commit=commit,
        )


def test_remote_tag_rebind_rejects_a_lightweight_tag(
    tmp_path: Path,
    release_tag_module: ModuleType,
) -> None:
    remote, source, _, _ = _remote_with_annotated_tag(tmp_path)
    lightweight = "v0.2.0"
    _git(source, "tag", lightweight)
    _git(source, "push", "origin", f"refs/tags/{lightweight}")
    commit = _git(source, "rev-parse", "HEAD")

    with pytest.raises(
        release_tag_module.RemoteTagError,
        match="moved or disappeared",
    ):
        release_tag_module.verify_remote_tag(
            repository=str(remote),
            tag=lightweight,
            tag_object=commit,
            commit=commit,
        )


def test_remote_tag_rebind_rejects_revision_option_shape(
    tmp_path: Path,
    release_tag_module: ModuleType,
) -> None:
    remote, _, tag_object, commit = _remote_with_annotated_tag(tmp_path)

    with pytest.raises(
        release_tag_module.RemoteTagError,
        match="unsupported shape",
    ):
        release_tag_module.verify_remote_tag(
            repository=str(remote),
            tag="--upload-pack=unexpected",
            tag_object=tag_object,
            commit=commit,
        )

    with pytest.raises(
        release_tag_module.RemoteTagError,
        match="non-empty single-line Git remote",
    ):
        release_tag_module.verify_remote_tag(
            repository="--upload-pack=unexpected",
            tag=_TAG,
            tag_object=tag_object,
            commit=commit,
        )
