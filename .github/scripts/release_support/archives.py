from __future__ import annotations

import subprocess
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from typing import BinaryIO, cast

from release_support.common import (
    HEX_IDENTIFIER,
    ProjectIdentity,
    ReleaseArtifactError,
    require,
    sha256_bytes,
    sha256_file,
)


def _safe_member_name(name: str) -> None:
    path = PurePosixPath(name)
    require(
        bool(name)
        and not path.is_absolute()
        and all(part not in ("", ".", "..") for part in path.parts),
        f"unsafe archive member path: {name!r}",
    )


def _inventory_entry(name: str, content: bytes) -> dict[str, object]:
    return {
        "path": name,
        "size": len(content),
        "sha256": sha256_bytes(content),
    }


def tar_inventory(path: Path) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    seen: set[str] = set()
    with tarfile.open(path, mode="r:gz") as archive:
        for member in archive.getmembers():
            _safe_member_name(member.name)
            require(member.name not in seen, f"duplicate sdist member: {member.name}")
            seen.add(member.name)
            require(
                member.isdir() or member.isfile(),
                f"unsupported sdist member kind: {member.name}",
            )
            if member.isfile():
                stream = archive.extractfile(member)
                require(stream is not None, f"unreadable sdist member: {member.name}")
                stream = cast(BinaryIO, stream)
                inventory.append(_inventory_entry(member.name, stream.read()))
    require(bool(inventory), "sdist has no regular-file members")
    return sorted(inventory, key=lambda item: str(item["path"]))


def wheel_inventory(path: Path) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            _safe_member_name(member.filename)
            require(
                member.filename not in seen,
                f"duplicate wheel member: {member.filename}",
            )
            seen.add(member.filename)
            if not member.is_dir():
                inventory.append(
                    _inventory_entry(member.filename, archive.read(member))
                )
    require(bool(inventory), "wheel has no file members")
    return sorted(inventory, key=lambda item: str(item["path"]))


def materialize_source_archive(
    *,
    repository: Path,
    commit: str,
    archive_path: Path,
    destination: Path,
) -> None:
    require(repository.is_dir(), "source repository is not a directory")
    require(
        HEX_IDENTIFIER.fullmatch(commit) is not None,
        "source commit must be a lowercase Git object identifier",
    )
    require(not archive_path.exists(), "source archive path already exists")
    require(not destination.exists(), "source destination already exists")
    require(
        destination.name not in ("", ".", ".."),
        "source destination has no safe archive prefix",
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with archive_path.open("xb") as stream:
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "archive",
                    "--format=tar",
                    f"--prefix={destination.name}/",
                    commit,
                ],
                check=True,
                stdout=stream,
            )
        tracked_bytes = subprocess.check_output(
            ["git", "-C", str(repository), "ls-files", "-z"],
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise ReleaseArtifactError(
            f"source archive Git operation failed: {error}"
        ) from error

    prefix = f"{destination.name}/"
    archived_files: set[str] = set()
    with tarfile.open(archive_path, mode="r:") as archive:
        for member in archive.getmembers():
            _safe_member_name(member.name)
            if member.name == destination.name and member.isdir():
                continue
            require(
                member.name.startswith(prefix),
                f"source archive member escaped its prefix: {member.name}",
            )
            relative_name = member.name.removeprefix(prefix)
            if member.isdir():
                continue
            require(
                member.isfile(),
                f"unsupported source archive member kind: {member.name}",
            )
            require(
                relative_name not in archived_files,
                f"duplicate source archive member: {relative_name}",
            )
            archived_files.add(relative_name)
        archive.extractall(destination.parent, filter="data")

    try:
        tracked_files = {
            item.decode("utf-8") for item in tracked_bytes.split(b"\0") if item
        }
    except UnicodeDecodeError as error:
        raise ReleaseArtifactError("tracked path is not valid UTF-8") from error
    require(
        archived_files == tracked_files,
        "tag archive inventory mismatch: "
        f"extra={sorted(archived_files - tracked_files)!r}, "
        f"missing={sorted(tracked_files - archived_files)!r}",
    )
    for name in tracked_files:
        require(
            (destination / name).read_bytes() == (repository / name).read_bytes(),
            f"tag archive byte mismatch: {name}",
        )


def _metadata_identity(metadata_bytes: bytes) -> ProjectIdentity:
    metadata = BytesParser().parsebytes(metadata_bytes)
    name = metadata.get("Name")
    version = metadata.get("Version")
    require(
        isinstance(name, str) and bool(name),
        "distribution metadata has no Name",
    )
    require(
        isinstance(version, str) and bool(version),
        "distribution metadata has no Version",
    )
    name = cast(str, name)
    version = cast(str, version)
    return ProjectIdentity(name=name, version=version)


def sdist_metadata(path: Path) -> ProjectIdentity:
    with tarfile.open(path, mode="r:gz") as archive:
        candidates = [
            member
            for member in archive.getmembers()
            if member.isfile()
            and len(PurePosixPath(member.name).parts) == 2
            and PurePosixPath(member.name).name == "PKG-INFO"
        ]
        require(
            len(candidates) == 1,
            f"sdist must contain one root PKG-INFO, found {len(candidates)}",
        )
        stream = archive.extractfile(candidates[0])
        require(stream is not None, "sdist PKG-INFO is unreadable")
        stream = cast(BinaryIO, stream)
        return _metadata_identity(stream.read())


def wheel_metadata(path: Path) -> ProjectIdentity:
    with zipfile.ZipFile(path) as archive:
        candidates = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        require(
            len(candidates) == 1,
            f"wheel must contain one METADATA, found {len(candidates)}",
        )
        return _metadata_identity(archive.read(candidates[0]))


def artifact_record(
    *,
    path: Path,
    kind: str,
    metadata: ProjectIdentity,
    inventory: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "filename": path.name,
        "kind": kind,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "metadata": {
            "name": metadata.name,
            "version": metadata.version,
        },
        "inventory": inventory,
    }
