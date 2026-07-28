from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import ModuleType

import pytest

from .support import (
    COMMIT,
    TAG_OBJECT,
    TREE,
    VERSION,
    prepare_candidate,
    verify_candidate,
    write_project,
    write_sdist,
    write_wheel,
)


def test_candidate_binds_exact_source_and_distribution_bytes(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    candidate_module, _, _ = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)

    evidence = verify_candidate(candidate_module, repository, candidate_directory)

    assert evidence["format"] == "belgi-python-release-evidence/v1"
    assert evidence["source"] == {
        "tag": f"v{VERSION}",
        "tagObject": TAG_OBJECT,
        "commit": COMMIT,
        "tree": TREE,
    }
    assert [item["kind"] for item in evidence["artifacts"]] == ["sdist", "wheel"]
    assert evidence["wheelReproducibility"]["matched"] is True


@pytest.mark.parametrize(
    ("field", "identifier"),
    (
        ("tag_object", "a" * 39),
        ("tag_object", "a" * 41),
        ("commit", "a" * 63),
        ("commit", "a" * 65),
        ("tree", "A" * 40),
    ),
)
def test_source_identity_rejects_non_git_object_identifiers(
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
    field: str,
    identifier: str,
) -> None:
    _, common_module, _ = release_modules
    identifiers = {
        "tag_object": TAG_OBJECT,
        "commit": COMMIT,
        "tree": TREE,
    }
    identifiers[field] = identifier

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="lowercase Git object identifier",
    ):
        common_module.validate_source_identity(
            identity=common_module.ProjectIdentity(
                name="belgi",
                version=VERSION,
            ),
            tag=f"v{VERSION}",
            tag_object=identifiers["tag_object"],
            commit=identifiers["commit"],
            tree=identifiers["tree"],
        )


@pytest.mark.parametrize("mutation", ("missing", "extra"))
def test_candidate_inventory_rejects_missing_and_extra_files(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
    mutation: str,
) -> None:
    candidate_module, common_module, _ = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    if mutation == "missing":
        (candidate_directory / "dist" / f"belgi-{VERSION}.tar.gz").unlink()
    else:
        (candidate_directory / "dist" / "unexpected.whl").write_bytes(b"extra")

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="candidate inventory mismatch",
    ):
        verify_candidate(candidate_module, repository, candidate_directory)


@pytest.mark.parametrize(
    ("metadata_name", "metadata_version"),
    (("other", VERSION), ("belgi", "9.9.9")),
)
def test_prepare_rejects_wrong_distribution_name_and_version(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
    metadata_name: str,
    metadata_version: str,
) -> None:
    candidate_module, common_module, _ = release_modules
    repository = tmp_path / "repository"
    write_project(repository)
    sdist_directory = tmp_path / "sdist"
    first_wheel_directory = tmp_path / "first"
    second_wheel_directory = tmp_path / "second"
    write_sdist(
        sdist_directory,
        metadata_name=metadata_name,
        metadata_version=metadata_version,
    )
    write_wheel(first_wheel_directory)
    write_wheel(second_wheel_directory)

    with pytest.raises(common_module.ReleaseArtifactError, match="metadata is"):
        candidate_module.prepare_candidate(
            repository=repository,
            sdist_directory=sdist_directory,
            first_wheel_directory=first_wheel_directory,
            second_wheel_directory=second_wheel_directory,
            candidate_directory=tmp_path / "candidate",
            tag=f"v{VERSION}",
            tag_object=TAG_OBJECT,
            commit=COMMIT,
            tree=TREE,
        )


def test_prepare_rejects_non_reproducible_wheels(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    candidate_module, common_module, _ = release_modules
    repository = tmp_path / "repository"
    write_project(repository)
    sdist_directory = tmp_path / "sdist"
    first_wheel_directory = tmp_path / "first"
    second_wheel_directory = tmp_path / "second"
    write_sdist(sdist_directory)
    write_wheel(first_wheel_directory)
    write_wheel(second_wheel_directory, source=b'__version__ = "changed"\n')

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="independently built wheels differ",
    ):
        candidate_module.prepare_candidate(
            repository=repository,
            sdist_directory=sdist_directory,
            first_wheel_directory=first_wheel_directory,
            second_wheel_directory=second_wheel_directory,
            candidate_directory=tmp_path / "candidate",
            tag=f"v{VERSION}",
            tag_object=TAG_OBJECT,
            commit=COMMIT,
            tree=TREE,
        )


def test_candidate_rejects_digest_drift(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    candidate_module, common_module, _ = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    wheel = candidate_directory / "dist" / f"belgi-{VERSION}-py3-none-any.whl"
    wheel.write_bytes(wheel.read_bytes() + b"changed")

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match=r"release-evidence\.json",
    ):
        verify_candidate(candidate_module, repository, candidate_directory)


def test_candidate_rejects_semantically_equal_noncanonical_evidence(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    candidate_module, common_module, _ = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    evidence_path = candidate_directory / "evidence" / "release-evidence.json"
    document = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence_path.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )
    evidence_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    checksums_path = candidate_directory / "evidence" / "SHA256SUMS"
    lines = checksums_path.read_text(encoding="ascii").splitlines()
    checksums_path.write_text(
        "\n".join(
            (
                f"{evidence_digest}  evidence/release-evidence.json"
                if line.endswith("  evidence/release-evidence.json")
                else line
            )
            for line in lines
        )
        + "\n",
        encoding="ascii",
    )

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="canonical exact evidence",
    ):
        verify_candidate(candidate_module, repository, candidate_directory)
