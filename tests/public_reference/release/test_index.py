from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest

from .support import (
    candidate_downloads,
    index_document,
    prepare_candidate,
    verify_candidate,
)


def _verify_payload(
    index_module: ModuleType,
    *,
    candidate_directory: Path,
    document: dict[str, object],
    downloads: dict[str, bytes],
) -> dict[str, object]:
    return index_module.verify_index_payload(
        candidate_directory=candidate_directory,
        index_document=document,
        download=lambda url, _expected_size: downloads[url],
        index_host="files.pythonhosted.org",
    )


def test_index_readback_accepts_only_exact_candidate_bytes(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    candidate_module, _, index_module = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    evidence = verify_candidate(candidate_module, repository, candidate_directory)
    document = index_document(evidence)
    downloads = candidate_downloads(candidate_directory, document)

    report = _verify_payload(
        index_module,
        candidate_directory=candidate_directory,
        document=document,
        downloads=downloads,
    )

    assert report["distribution"] == {"name": "belgi", "version": "0.1.0a0"}
    assert len(report["files"]) == 2


def test_index_readback_rejects_changed_bytes(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    candidate_module, common_module, index_module = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    evidence = verify_candidate(candidate_module, repository, candidate_directory)
    document = index_document(evidence)
    downloads = candidate_downloads(candidate_directory, document)
    first_url = next(iter(downloads))
    downloads[first_url] += b"changed"

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="read-back size differs",
    ):
        _verify_payload(
            index_module,
            candidate_directory=candidate_directory,
            document=document,
            downloads=downloads,
        )


@pytest.mark.parametrize("mutation", ("duplicate", "unexpected"))
def test_index_readback_rejects_duplicate_and_unexpected_files(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
    mutation: str,
) -> None:
    candidate_module, common_module, index_module = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    evidence = verify_candidate(candidate_module, repository, candidate_directory)
    document = index_document(evidence)
    downloads = candidate_downloads(candidate_directory, document)
    urls = document["urls"]
    assert isinstance(urls, list)
    if mutation == "duplicate":
        urls[1] = dict(urls[0])
    else:
        assert isinstance(urls[1], dict)
        urls[1]["filename"] = "unexpected.whl"

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match=r"duplicate index file|unexpected index file",
    ):
        _verify_payload(
            index_module,
            candidate_directory=candidate_directory,
            document=document,
            downloads=downloads,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("digests", {"sha256": "0" * 64}, "index digest mismatch"),
        ("size", 0, "index size mismatch"),
    ),
)
def test_index_readback_rejects_advertised_identity_mismatch(
    tmp_path: Path,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
    field: str,
    value: object,
    message: str,
) -> None:
    candidate_module, common_module, index_module = release_modules
    repository, candidate_directory = prepare_candidate(tmp_path, candidate_module)
    evidence = verify_candidate(candidate_module, repository, candidate_directory)
    document = index_document(evidence)
    urls = document["urls"]
    assert isinstance(urls, list) and isinstance(urls[0], dict)
    urls[0][field] = value
    downloads = candidate_downloads(candidate_directory, document)

    with pytest.raises(common_module.ReleaseArtifactError, match=message):
        _verify_payload(
            index_module,
            candidate_directory=candidate_directory,
            document=document,
            downloads=downloads,
        )


class _Response:
    def __init__(
        self,
        *,
        final_url: str,
        content: bytes,
        content_length: str | None = None,
    ) -> None:
        self.headers = (
            {} if content_length is None else {"Content-Length": content_length}
        )
        self._final_url = final_url
        self._content = content
        self.read_sizes: list[int] = []

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_arguments: object) -> None:
        return None

    def geturl(self) -> str:
        return self._final_url

    def read(self, size: int) -> bytes:
        self.read_sizes.append(size)
        return self._content[:size]


def test_network_read_is_bounded_even_without_content_length(
    monkeypatch: pytest.MonkeyPatch,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    _, common_module, index_module = release_modules
    response = _Response(
        final_url="https://files.pythonhosted.org/file",
        content=b"x" * 9,
    )
    monkeypatch.setattr(
        index_module,
        "_open_url",
        lambda *_arguments, **_keywords: response,
    )

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="response exceeds read bound",
    ):
        index_module.read_url_bounded(
            "https://files.pythonhosted.org/file",
            8,
            allowed_host="files.pythonhosted.org",
        )
    assert response.read_sizes == [9]


def test_network_read_rejects_redirect_outside_allowed_host(
    monkeypatch: pytest.MonkeyPatch,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    _, common_module, index_module = release_modules
    response = _Response(
        final_url="https://other.example/file",
        content=b"candidate",
    )
    monkeypatch.setattr(
        index_module,
        "_open_url",
        lambda *_arguments, **_keywords: response,
    )

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="escaped the allowed host",
    ):
        index_module.read_url_bounded(
            "https://files.pythonhosted.org/file",
            9,
            allowed_host="files.pythonhosted.org",
        )
    assert response.read_sizes == []


def test_network_read_rejects_disallowed_intermediate_redirect_hop(
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
) -> None:
    _, common_module, index_module = release_modules
    handler = index_module._ConfinedRedirectHandler("files.pythonhosted.org")
    request = index_module.urllib.request.Request(
        "https://files.pythonhosted.org/start"
    )

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match="escaped the allowed host",
    ):
        handler.redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://evil.example/intermediate",
        )


@pytest.mark.parametrize("content_length", ("not-a-number", "-1", "10"))
def test_network_read_rejects_invalid_or_out_of_bound_content_length(
    monkeypatch: pytest.MonkeyPatch,
    release_modules: tuple[ModuleType, ModuleType, ModuleType],
    content_length: str,
) -> None:
    _, common_module, index_module = release_modules
    response = _Response(
        final_url="https://files.pythonhosted.org/file",
        content=b"candidate",
        content_length=content_length,
    )
    monkeypatch.setattr(
        index_module,
        "_open_url",
        lambda *_arguments, **_keywords: response,
    )

    with pytest.raises(
        common_module.ReleaseArtifactError,
        match=r"invalid Content-Length|outside the read bound",
    ):
        index_module.read_url_bounded(
            "https://files.pythonhosted.org/file",
            9,
            allowed_host="files.pythonhosted.org",
        )
    assert response.read_sizes == []
