from __future__ import annotations

import json
import shutil
from pathlib import Path

from release_support.archives import (
    artifact_record,
    sdist_metadata,
    tar_inventory,
    wheel_inventory,
    wheel_metadata,
)
from release_support.common import (
    EVIDENCE_FORMAT,
    SHA256,
    ProjectIdentity,
    canonical_json_bytes,
    read_project_identity,
    require,
    sha256_file,
    validate_source_identity,
)


def _single_file(directory: Path, expected_name: str, label: str) -> Path:
    entries = sorted(path.name for path in directory.iterdir())
    require(
        entries == [expected_name] and (directory / expected_name).is_file(),
        f"{label} inventory must be [{expected_name!r}], found {entries!r}",
    )
    return directory / expected_name


def _validate_artifact_metadata(
    actual: ProjectIdentity,
    expected: ProjectIdentity,
    *,
    label: str,
) -> None:
    require(
        actual == expected,
        f"{label} metadata is {actual.name} {actual.version}, "
        f"expected {expected.name} {expected.version}",
    )


def validate_sdist(*, repository: Path, sdist_directory: Path) -> Path:
    identity = read_project_identity(repository)
    sdist = _single_file(
        sdist_directory,
        identity.sdist_filename,
        "sdist",
    )
    _validate_artifact_metadata(sdist_metadata(sdist), identity, label="sdist")
    tar_inventory(sdist)
    return sdist


def _expected_evidence(
    *,
    identity: ProjectIdentity,
    tag: str,
    tag_object: str,
    commit: str,
    tree: str,
    sdist: Path,
    wheel: Path,
) -> dict[str, object]:
    wheel_digest = sha256_file(wheel)
    return {
        "format": EVIDENCE_FORMAT,
        "distribution": {
            "name": identity.name,
            "version": identity.version,
        },
        "source": {
            "tag": tag,
            "tagObject": tag_object,
            "commit": commit,
            "tree": tree,
        },
        "wheelReproducibility": {
            "firstSha256": wheel_digest,
            "secondSha256": wheel_digest,
            "matched": True,
        },
        "artifacts": [
            artifact_record(
                path=sdist,
                kind="sdist",
                metadata=sdist_metadata(sdist),
                inventory=tar_inventory(sdist),
            ),
            artifact_record(
                path=wheel,
                kind="wheel",
                metadata=wheel_metadata(wheel),
                inventory=wheel_inventory(wheel),
            ),
        ],
    }


def prepare_candidate(
    *,
    repository: Path,
    sdist_directory: Path,
    first_wheel_directory: Path,
    second_wheel_directory: Path,
    candidate_directory: Path,
    tag: str,
    tag_object: str,
    commit: str,
    tree: str,
) -> None:
    identity = read_project_identity(repository)
    validate_source_identity(
        identity=identity,
        tag=tag,
        tag_object=tag_object,
        commit=commit,
        tree=tree,
    )
    sdist = validate_sdist(
        repository=repository,
        sdist_directory=sdist_directory,
    )
    first_wheel = _single_file(
        first_wheel_directory,
        identity.wheel_filename,
        "first wheel",
    )
    second_wheel = _single_file(
        second_wheel_directory,
        identity.wheel_filename,
        "second wheel",
    )
    _validate_artifact_metadata(sdist_metadata(sdist), identity, label="sdist")
    _validate_artifact_metadata(
        wheel_metadata(first_wheel),
        identity,
        label="first wheel",
    )
    _validate_artifact_metadata(
        wheel_metadata(second_wheel),
        identity,
        label="second wheel",
    )
    require(
        sha256_file(first_wheel) == sha256_file(second_wheel),
        "independently built wheels differ",
    )
    require(
        not candidate_directory.exists()
        or (candidate_directory.is_dir() and not any(candidate_directory.iterdir())),
        "candidate directory must be empty",
    )
    dist = candidate_directory / "dist"
    evidence_directory = candidate_directory / "evidence"
    dist.mkdir(parents=True, exist_ok=True)
    evidence_directory.mkdir(parents=True, exist_ok=True)
    admitted_sdist = dist / sdist.name
    admitted_wheel = dist / first_wheel.name
    shutil.copyfile(sdist, admitted_sdist)
    shutil.copyfile(first_wheel, admitted_wheel)

    evidence = _expected_evidence(
        identity=identity,
        tag=tag,
        tag_object=tag_object,
        commit=commit,
        tree=tree,
        sdist=admitted_sdist,
        wheel=admitted_wheel,
    )
    evidence_path = evidence_directory / "release-evidence.json"
    evidence_path.write_bytes(canonical_json_bytes(evidence))
    checksum_entries = [
        (sha256_file(admitted_sdist), f"dist/{admitted_sdist.name}"),
        (sha256_file(admitted_wheel), f"dist/{admitted_wheel.name}"),
        (sha256_file(evidence_path), "evidence/release-evidence.json"),
    ]
    checksum_text = "".join(
        f"{digest}  {name}\n" for digest, name in sorted(checksum_entries)
    )
    (evidence_directory / "SHA256SUMS").write_text(
        checksum_text,
        encoding="ascii",
        newline="\n",
    )
    verify_candidate(
        repository=repository,
        candidate_directory=candidate_directory,
        tag=tag,
        tag_object=tag_object,
        commit=commit,
        tree=tree,
    )


def _candidate_file_names(candidate_directory: Path) -> list[str]:
    return sorted(
        path.relative_to(candidate_directory).as_posix()
        for path in candidate_directory.rglob("*")
        if path.is_file()
    )


def _parse_checksums(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split("  ", maxsplit=1)
        require(len(parts) == 2, f"malformed SHA256SUMS line: {line!r}")
        digest, name = parts
        require(SHA256.fullmatch(digest) is not None, "invalid SHA-256 digest")
        require(name not in entries, f"duplicate SHA256SUMS entry: {name}")
        entries[name] = digest
    return entries


def verify_candidate(
    *,
    repository: Path,
    candidate_directory: Path,
    tag: str,
    tag_object: str,
    commit: str,
    tree: str,
) -> dict[str, object]:
    identity = read_project_identity(repository)
    validate_source_identity(
        identity=identity,
        tag=tag,
        tag_object=tag_object,
        commit=commit,
        tree=tree,
    )
    expected_files = [
        f"dist/{identity.sdist_filename}",
        f"dist/{identity.wheel_filename}",
        "evidence/SHA256SUMS",
        "evidence/release-evidence.json",
    ]
    actual_files = _candidate_file_names(candidate_directory)
    require(
        actual_files == sorted(expected_files),
        f"candidate inventory mismatch: {actual_files!r}",
    )

    sdist = candidate_directory / "dist" / identity.sdist_filename
    wheel = candidate_directory / "dist" / identity.wheel_filename
    evidence_path = candidate_directory / "evidence" / "release-evidence.json"
    evidence_bytes = evidence_path.read_bytes()
    evidence = json.loads(evidence_bytes.decode("utf-8"))
    expected_evidence = _expected_evidence(
        identity=identity,
        tag=tag,
        tag_object=tag_object,
        commit=commit,
        tree=tree,
        sdist=sdist,
        wheel=wheel,
    )
    require(
        evidence == expected_evidence,
        "release-evidence.json does not describe the exact candidate bytes",
    )
    require(
        evidence_bytes == canonical_json_bytes(expected_evidence),
        "release-evidence.json is not the canonical exact evidence document",
    )

    checksums = _parse_checksums(candidate_directory / "evidence" / "SHA256SUMS")
    expected_checksums = {
        f"dist/{sdist.name}": sha256_file(sdist),
        f"dist/{wheel.name}": sha256_file(wheel),
        "evidence/release-evidence.json": sha256_file(evidence_path),
    }
    require(
        checksums == expected_checksums,
        "SHA256SUMS does not bind the exact candidate files",
    )
    return evidence
