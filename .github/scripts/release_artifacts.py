#!/usr/bin/env python3
"""Admit and read back one exact BELGI Python release candidate."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from release_support.archives import materialize_source_archive
from release_support.candidate import (
    prepare_candidate,
    validate_sdist,
    verify_candidate,
)
from release_support.common import ReleaseArtifactError, require
from release_support.index import read_back_index
from release_support.installed import verify_installed_journey


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--repository", type=Path, required=True)
    prepare.add_argument("--sdist-directory", type=Path, required=True)
    prepare.add_argument("--first-wheel-directory", type=Path, required=True)
    prepare.add_argument("--second-wheel-directory", type=Path, required=True)
    prepare.add_argument("--candidate-directory", type=Path, required=True)
    prepare.add_argument("--tag", required=True)
    prepare.add_argument("--tag-object", required=True)
    prepare.add_argument("--commit", required=True)
    prepare.add_argument("--tree", required=True)

    materialize = subparsers.add_parser("materialize-source")
    materialize.add_argument("--repository", type=Path, required=True)
    materialize.add_argument("--commit", required=True)
    materialize.add_argument("--archive", type=Path, required=True)
    materialize.add_argument("--destination", type=Path, required=True)

    sdist = subparsers.add_parser("validate-sdist")
    sdist.add_argument("--repository", type=Path, required=True)
    sdist.add_argument("--sdist-directory", type=Path, required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--repository", type=Path, required=True)
    verify.add_argument("--candidate-directory", type=Path, required=True)
    verify.add_argument("--tag", required=True)
    verify.add_argument("--tag-object", required=True)
    verify.add_argument("--commit", required=True)
    verify.add_argument("--tree", required=True)

    readback = subparsers.add_parser("readback")
    readback.add_argument("--candidate-directory", type=Path, required=True)
    readback.add_argument("--index-base-url", required=True)
    readback.add_argument("--file-host", required=True)
    readback.add_argument("--output", type=Path, required=True)
    readback.add_argument("--attempts", type=int, default=20)
    readback.add_argument("--delay-seconds", type=float, default=6.0)

    installed = subparsers.add_parser("installed")
    installed.add_argument("--environment", type=Path, required=True)
    installed.add_argument("--expected-version", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.command == "prepare":
        prepare_candidate(
            repository=arguments.repository.resolve(strict=True),
            sdist_directory=arguments.sdist_directory.resolve(strict=True),
            first_wheel_directory=arguments.first_wheel_directory.resolve(strict=True),
            second_wheel_directory=arguments.second_wheel_directory.resolve(
                strict=True
            ),
            candidate_directory=arguments.candidate_directory.resolve(),
            tag=arguments.tag,
            tag_object=arguments.tag_object,
            commit=arguments.commit,
            tree=arguments.tree,
        )
    elif arguments.command == "materialize-source":
        materialize_source_archive(
            repository=arguments.repository.resolve(strict=True),
            commit=arguments.commit,
            archive_path=arguments.archive.resolve(),
            destination=arguments.destination.resolve(),
        )
    elif arguments.command == "validate-sdist":
        validate_sdist(
            repository=arguments.repository.resolve(strict=True),
            sdist_directory=arguments.sdist_directory.resolve(strict=True),
        )
    elif arguments.command == "verify":
        verify_candidate(
            repository=arguments.repository.resolve(strict=True),
            candidate_directory=arguments.candidate_directory.resolve(strict=True),
            tag=arguments.tag,
            tag_object=arguments.tag_object,
            commit=arguments.commit,
            tree=arguments.tree,
        )
    elif arguments.command == "readback":
        require(arguments.attempts > 0, "attempt count must be positive")
        require(
            arguments.delay_seconds >= 0,
            "read-back delay must be non-negative",
        )
        read_back_index(
            candidate_directory=arguments.candidate_directory.resolve(strict=True),
            index_base_url=arguments.index_base_url,
            file_host=arguments.file_host,
            output=arguments.output,
            attempts=arguments.attempts,
            delay_seconds=arguments.delay_seconds,
        )
    else:
        verify_installed_journey(
            environment=arguments.environment.resolve(strict=True),
            expected_version=arguments.expected_version,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReleaseArtifactError as error:
        print(f"RELEASE_ARTIFACT_ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
