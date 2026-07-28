from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, cast

from release_support.common import (
    ReleaseArtifactError,
    canonical_json_bytes,
    require,
    sha256_bytes,
)

_MAX_INDEX_DOCUMENT_BYTES = 1024 * 1024
_USER_AGENT = "belgi-release-readback/1"


class _ConfinedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_host: str) -> None:
        super().__init__()
        self._allowed_host = allowed_host

    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: Any,
        code: int,
        message: str,
        headers: Any,
        new_url: str,
    ) -> urllib.request.Request | None:
        _require_https_host(new_url, self._allowed_host)
        return super().redirect_request(
            request,
            file_pointer,
            code,
            message,
            headers,
            new_url,
        )


def _open_url(
    request: urllib.request.Request,
    *,
    allowed_host: str,
    timeout: int,
) -> Any:
    opener = urllib.request.build_opener(_ConfinedRedirectHandler(allowed_host))
    return opener.open(request, timeout=timeout)


def verify_index_payload(
    *,
    candidate_directory: Path,
    index_document: Mapping[str, Any],
    download: Callable[[str, int], bytes],
    index_host: str,
) -> dict[str, object]:
    evidence = json.loads(
        (candidate_directory / "evidence" / "release-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    distribution = evidence.get("distribution")
    artifacts = evidence.get("artifacts")
    require(isinstance(distribution, dict), "evidence distribution is missing")
    require(isinstance(artifacts, list), "evidence artifacts are missing")
    distribution = cast(dict[str, object], distribution)
    artifacts = cast(list[object], artifacts)
    name = distribution.get("name")
    version = distribution.get("version")
    require(isinstance(name, str), "evidence project name is missing")
    require(isinstance(version, str), "evidence project version is missing")
    name = cast(str, name)
    version = cast(str, version)

    info = index_document.get("info")
    urls = index_document.get("urls")
    require(isinstance(info, dict), "index response has no info object")
    info = cast(dict[str, object], info)
    require(info.get("name") == name, "index project name mismatch")
    require(info.get("version") == version, "index project version mismatch")
    require(isinstance(urls, list), "index response has no file list")
    urls = cast(list[object], urls)

    expected: dict[str, dict[str, object]] = {}
    for raw_artifact in artifacts:
        require(
            isinstance(raw_artifact, dict),
            "evidence artifact entry is not an object",
        )
        artifact = cast(dict[str, object], raw_artifact)
        filename = artifact.get("filename")
        require(isinstance(filename, str), "evidence artifact has no filename")
        filename = cast(str, filename)
        require(
            filename not in expected,
            f"duplicate evidence artifact: {filename}",
        )
        expected[filename] = artifact
    require(len(expected) == 2, "evidence must describe exactly two artifacts")
    require(
        len(urls) == len(expected),
        f"index must expose exactly {len(expected)} files, found {len(urls)}",
    )
    observed: dict[str, dict[str, object]] = {}
    expected_types = {"sdist": "sdist", "wheel": "bdist_wheel"}
    for raw_entry in urls:
        require(isinstance(raw_entry, dict), "index file entry is not an object")
        entry = cast(dict[str, object], raw_entry)
        filename = entry.get("filename")
        require(isinstance(filename, str), "index file has no filename")
        filename = cast(str, filename)
        require(filename not in observed, f"duplicate index file: {filename}")
        require(filename in expected, f"unexpected index file: {filename}")
        artifact = expected[filename]
        artifact_kind = artifact.get("kind")
        require(
            isinstance(artifact_kind, str) and artifact_kind in expected_types,
            f"candidate kind is invalid for {filename}",
        )
        artifact_kind = cast(str, artifact_kind)
        expected_kind = expected_types[artifact_kind]
        expected_digest = artifact.get("sha256")
        expected_size = artifact.get("size")
        require(
            isinstance(expected_digest, str),
            f"candidate digest is invalid for {filename}",
        )
        require(
            isinstance(expected_size, int) and expected_size >= 0,
            f"candidate size is invalid for {filename}",
        )
        expected_digest = cast(str, expected_digest)
        expected_size = cast(int, expected_size)
        require(
            entry.get("packagetype") == expected_kind,
            f"index file kind mismatch for {filename}",
        )
        require(entry.get("yanked") is False, f"index file is yanked: {filename}")
        digests = entry.get("digests")
        require(isinstance(digests, dict), f"index file has no digests: {filename}")
        digests = cast(dict[str, object], digests)
        require(
            digests.get("sha256") == expected_digest,
            f"index digest mismatch for {filename}",
        )
        require(
            entry.get("size") == expected_size,
            f"index size mismatch for {filename}",
        )
        url = entry.get("url")
        require(isinstance(url, str), f"index file has no URL: {filename}")
        url = cast(str, url)
        _require_https_host(url, index_host)
        content = download(url, expected_size)
        require(
            len(content) == expected_size,
            f"read-back size differs for {filename}",
        )
        require(
            sha256_bytes(content) == expected_digest,
            f"read-back bytes differ for {filename}",
        )
        observed[filename] = {
            "filename": filename,
            "size": len(content),
            "sha256": sha256_bytes(content),
            "url": url,
        }
    require(set(observed) == set(expected), "index file inventory is incomplete")
    return {
        "format": "belgi-python-index-readback/v1",
        "distribution": {"name": name, "version": version},
        "files": [observed[name] for name in sorted(observed)],
    }


def read_url_bounded(
    url: str,
    maximum_bytes: int,
    *,
    allowed_host: str,
    expected_size: int | None = None,
) -> bytes:
    require(maximum_bytes >= 0, "read bound must be non-negative")
    if expected_size is not None:
        require(
            0 <= expected_size <= maximum_bytes,
            "expected response size exceeds read bound",
        )
    _require_https_host(url, allowed_host)
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with _open_url(request, allowed_host=allowed_host, timeout=30) as response:
        _require_https_host(response.geturl(), allowed_host)
        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError as error:
                raise ReleaseArtifactError(
                    f"invalid Content-Length for {url}"
                ) from error
            require(
                0 <= declared_size <= maximum_bytes,
                f"declared response size is outside the read bound for {url}",
            )
            if expected_size is not None:
                require(
                    declared_size == expected_size,
                    f"declared response size differs for {url}",
                )
        content = response.read(maximum_bytes + 1)
    require(
        len(content) <= maximum_bytes,
        f"response exceeds read bound for {url}",
    )
    if expected_size is not None:
        require(
            len(content) == expected_size,
            f"response size differs for {url}",
        )
    return content


def _require_https_host(url: str, allowed_host: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == "https", f"response URL is not HTTPS: {url}")
    require(
        parsed.hostname == allowed_host
        and parsed.username is None
        and parsed.password is None
        and parsed.port in (None, 443),
        f"response URL escaped the allowed host {allowed_host}: {url}",
    )


def read_back_index(
    *,
    candidate_directory: Path,
    index_base_url: str,
    file_host: str,
    output: Path,
    attempts: int,
    delay_seconds: float,
) -> None:
    evidence = json.loads(
        (candidate_directory / "evidence" / "release-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    distribution = evidence["distribution"]
    name = distribution["name"]
    version = distribution["version"]
    endpoint = f"{index_base_url.rstrip('/')}/pypi/{name}/{version}/json"
    parsed_index_host = urllib.parse.urlsplit(index_base_url).hostname
    require(isinstance(parsed_index_host, str), "index base URL has no host")
    index_host = cast(str, parsed_index_host)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            index_document = json.loads(
                read_url_bounded(
                    endpoint,
                    _MAX_INDEX_DOCUMENT_BYTES,
                    allowed_host=index_host,
                ).decode("utf-8")
            )
            result = verify_index_payload(
                candidate_directory=candidate_directory,
                index_document=index_document,
                download=lambda url, size: read_url_bounded(
                    url,
                    size,
                    allowed_host=file_host,
                    expected_size=size,
                ),
                index_host=file_host,
            )
            output.write_bytes(canonical_json_bytes(result))
            return
        except (
            json.JSONDecodeError,
            ReleaseArtifactError,
            UnicodeDecodeError,
            urllib.error.URLError,
        ) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(delay_seconds)
    raise ReleaseArtifactError(
        f"index read-back failed after {attempts} attempts: {last_error}"
    )
