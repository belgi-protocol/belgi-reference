#!/usr/bin/env python3
"""Rebind one remote annotated release tag to admitted Git object IDs."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence

_OBJECT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_RELEASE_TAG = re.compile(r"v[0-9A-Za-z][0-9A-Za-z._-]*")


class RemoteTagError(ValueError):
    """Raised when a remote tag is not the admitted annotated tag."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RemoteTagError(message)


def _object_id(value: str, label: str) -> str:
    _require(
        _OBJECT_ID.fullmatch(value) is not None,
        f"{label} must be a lowercase Git object identifier",
    )
    return value


def verify_remote_tag(
    *,
    repository: str,
    tag: str,
    tag_object: str,
    commit: str,
) -> None:
    _require(
        bool(repository)
        and not repository.startswith("-")
        and not any(ord(character) < 0x20 for character in repository),
        "repository must be a non-empty single-line Git remote",
    )
    _require(
        _RELEASE_TAG.fullmatch(tag) is not None,
        "release tag has an unsupported shape",
    )
    tag_object = _object_id(tag_object, "tag object")
    commit = _object_id(commit, "commit")
    tag_reference = f"refs/tags/{tag}"
    try:
        completed = subprocess.run(
            [
                "git",
                "ls-remote",
                repository,
                tag_reference,
                f"{tag_reference}^{{}}",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RemoteTagError(f"remote tag lookup failed: {error}") from error

    references: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        fields = line.split("\t")
        _require(len(fields) == 2, "remote tag lookup returned a malformed line")
        identifier, reference = fields
        _object_id(identifier, "remote object")
        _require(
            reference not in references,
            "remote tag lookup returned a duplicate reference",
        )
        references[reference] = identifier
    expected = {
        tag_reference: tag_object,
        f"{tag_reference}^{{}}": commit,
    }
    _require(
        references == expected,
        f"remote annotated tag moved or disappeared: {references!r}",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--tag-object", required=True)
    parser.add_argument("--commit", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    verify_remote_tag(
        repository=arguments.repository,
        tag=arguments.tag,
        tag_object=arguments.tag_object,
        commit=arguments.commit,
    )
    print(f"REMOTE_TAG_REBIND_OK tag={arguments.tag}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RemoteTagError as error:
        print(f"REMOTE_TAG_ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
