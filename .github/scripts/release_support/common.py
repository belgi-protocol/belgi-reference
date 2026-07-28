from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

EVIDENCE_FORMAT = "belgi-python-release-evidence/v1"
HEX_IDENTIFIER = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
SHA256 = re.compile(r"[0-9a-f]{64}")


class ReleaseArtifactError(ValueError):
    """Raised when release bytes do not satisfy the release contract."""


@dataclass(frozen=True)
class ProjectIdentity:
    name: str
    version: str

    @property
    def tag(self) -> str:
        return f"v{self.version}"

    @property
    def sdist_filename(self) -> str:
        return f"{self.name}-{self.version}.tar.gz"

    @property
    def wheel_filename(self) -> str:
        wheel_name = self.name.replace("-", "_")
        return f"{wheel_name}-{self.version}-py3-none-any.whl"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseArtifactError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def read_project_identity(repository: Path) -> ProjectIdentity:
    project_document = tomllib.loads(
        (repository / "pyproject.toml").read_text(encoding="utf-8")
    )
    raw_project = project_document.get("project")
    require(isinstance(raw_project, dict), "pyproject.toml has no project table")
    project = cast(dict[str, object], raw_project)
    name = project.get("name")
    version = project.get("version")
    require(isinstance(name, str) and bool(name), "project name is missing")
    require(
        isinstance(version, str) and bool(version),
        "project version is missing",
    )
    name = cast(str, name)
    version = cast(str, version)
    return ProjectIdentity(name=name, version=version)


def validate_source_identity(
    *,
    identity: ProjectIdentity,
    tag: str,
    tag_object: str,
    commit: str,
    tree: str,
) -> None:
    require(tag == identity.tag, f"tag must be {identity.tag!r}, found {tag!r}")
    require(
        HEX_IDENTIFIER.fullmatch(tag_object) is not None,
        "tag object must be a lowercase Git object identifier",
    )
    require(
        HEX_IDENTIFIER.fullmatch(commit) is not None,
        "commit must be a lowercase Git object identifier",
    )
    require(
        HEX_IDENTIFIER.fullmatch(tree) is not None,
        "tree must be a lowercase Git object identifier",
    )
