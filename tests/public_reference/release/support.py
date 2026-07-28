from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path
from types import ModuleType

COMMIT = "a" * 40
TAG_OBJECT = "c" * 40
TREE = "b" * 40
VERSION = "0.1.0a0"


def write_project(repository: Path) -> None:
    repository.mkdir()
    (repository / "pyproject.toml").write_text(
        '[project]\nname = "belgi"\nversion = "0.1.0a0"\n',
        encoding="utf-8",
    )


def metadata(*, name: str = "belgi", version: str = VERSION) -> bytes:
    return f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n\n".encode()


def write_sdist(
    directory: Path,
    *,
    metadata_name: str = "belgi",
    metadata_version: str = VERSION,
) -> Path:
    directory.mkdir()
    path = directory / f"belgi-{VERSION}.tar.gz"
    with tarfile.open(path, mode="w:gz") as archive:
        for name, content in (
            (
                f"belgi-{VERSION}/PKG-INFO",
                metadata(name=metadata_name, version=metadata_version),
            ),
            (f"belgi-{VERSION}/belgi/__init__.py", b'__version__ = "0.1.0a0"\n'),
        ):
            member = tarfile.TarInfo(name)
            member.size = len(content)
            member.mtime = 0
            member.mode = 0o644
            archive.addfile(member, io.BytesIO(content))
    return path


def write_wheel(
    directory: Path,
    *,
    metadata_name: str = "belgi",
    metadata_version: str = VERSION,
    source: bytes = b'__version__ = "0.1.0a0"\n',
) -> Path:
    directory.mkdir()
    path = directory / f"belgi-{VERSION}-py3-none-any.whl"
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("belgi/__init__.py", source)
        archive.writestr(
            f"belgi-{VERSION}.dist-info/METADATA",
            metadata(name=metadata_name, version=metadata_version),
        )
    return path


def prepare_candidate(
    tmp_path: Path,
    candidate_module: ModuleType,
) -> tuple[Path, Path]:
    repository = tmp_path / "repository"
    write_project(repository)
    sdist_directory = tmp_path / "sdist"
    first_wheel_directory = tmp_path / "first"
    second_wheel_directory = tmp_path / "second"
    write_sdist(sdist_directory)
    write_wheel(first_wheel_directory)
    write_wheel(second_wheel_directory)
    candidate_directory = tmp_path / "candidate"
    candidate_module.prepare_candidate(
        repository=repository,
        sdist_directory=sdist_directory,
        first_wheel_directory=first_wheel_directory,
        second_wheel_directory=second_wheel_directory,
        candidate_directory=candidate_directory,
        tag=f"v{VERSION}",
        tag_object=TAG_OBJECT,
        commit=COMMIT,
        tree=TREE,
    )
    return repository, candidate_directory


def verify_candidate(
    candidate_module: ModuleType,
    repository: Path,
    candidate_directory: Path,
) -> dict[str, object]:
    return candidate_module.verify_candidate(
        repository=repository,
        candidate_directory=candidate_directory,
        tag=f"v{VERSION}",
        tag_object=TAG_OBJECT,
        commit=COMMIT,
        tree=TREE,
    )


def index_document(
    evidence: dict[str, object],
    *,
    host: str = "files.pythonhosted.org",
) -> dict[str, object]:
    distribution = evidence["distribution"]
    assert isinstance(distribution, dict)
    artifacts = evidence["artifacts"]
    assert isinstance(artifacts, list)
    urls: list[dict[str, object]] = []
    for artifact in artifacts:
        assert isinstance(artifact, dict)
        filename = str(artifact["filename"])
        urls.append(
            {
                "filename": filename,
                "packagetype": (
                    "sdist" if artifact["kind"] == "sdist" else "bdist_wheel"
                ),
                "digests": {"sha256": artifact["sha256"]},
                "size": artifact["size"],
                "url": f"https://{host}/packages/{filename}",
                "yanked": False,
            }
        )
    return {
        "info": {
            "name": distribution["name"],
            "version": distribution["version"],
        },
        "urls": urls,
    }


def candidate_downloads(
    candidate_directory: Path,
    document: dict[str, object],
) -> dict[str, bytes]:
    urls = document["urls"]
    assert isinstance(urls, list)
    return {
        str(entry["url"]): (
            candidate_directory / "dist" / str(entry["filename"])
        ).read_bytes()
        for entry in urls
        if isinstance(entry, dict)
    }
