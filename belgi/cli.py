from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from enum import IntEnum
from pathlib import Path
from typing import NoReturn

from belgi.replay.package_source.exceptions import UnsupportedPackagePathKindError
from belgi.replay.procedure.public import run_public_replay
from belgi.replay.report_document import replay_report_to_json_object
from belgi.substrate.io.json.encoding import canonical_json_text


class _ExitCode(IntEnum):
    SUCCESS = 0
    REJECTED = 1
    USAGE = 2
    INTEGRATION = 3


class _UsageError(ValueError):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _UsageError(message)


def _parser() -> _Parser:
    parser = _Parser(
        prog="belgi",
        description="BELGI exact-edition replay reference implementation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_mode",
        help="emit one JSON document",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    replay = commands.add_parser(
        "replay",
        help="replay one physical directory or ZIP package",
    )
    replay.add_argument("path", metavar="PATH")
    commands.add_parser(
        "conformance",
        help="run installed normative corpora and implementation checks",
    )
    return parser


def _root_json_requested(argv: Sequence[str]) -> bool:
    root_options: list[str] = []
    for argument in argv:
        if argument == "--" or not argument.startswith("-"):
            break
        root_options.append(argument)
    return "--json" in root_options


def _write(
    *,
    document: Mapping[str, object],
    lines: Sequence[str],
    json_mode: bool,
    error: bool = False,
) -> None:
    if json_mode:
        sys.stdout.write(canonical_json_text(document) + "\n")
        return
    stream = sys.stderr if error else sys.stdout
    for line in lines:
        print(line, file=stream)


def _run_replay(*, package_path: Path, json_mode: bool) -> int:
    try:
        observation = run_public_replay(package_path=package_path)
    except UnsupportedPackagePathKindError as exc:
        document = {
            "detail": str(exc),
            "error_type": type(exc).__name__,
            "status": "unsupported-path-kind",
        }
        _write(
            document=document,
            lines=(f"ERROR replay {exc}",),
            json_mode=json_mode,
            error=True,
        )
        return _ExitCode.USAGE
    except OSError as exc:
        document = {
            "detail": str(exc),
            "error_type": type(exc).__name__,
            "status": "io-error",
        }
        _write(
            document=document,
            lines=(f"ERROR replay {exc}",),
            json_mode=json_mode,
            error=True,
        )
        return _ExitCode.INTEGRATION
    except Exception as exc:
        document = {
            "detail": str(exc),
            "error_type": type(exc).__name__,
            "status": "integration-error",
        }
        _write(
            document=document,
            lines=(f"ERROR replay {exc}",),
            json_mode=json_mode,
            error=True,
        )
        return _ExitCode.INTEGRATION

    execution = observation.execution
    representation = observation.representation_result
    if execution is None:
        if representation is None or representation.accepted:
            document = {
                "detail": "physical replay ended without a typed result",
                "error_type": "ReplayIntegrationError",
                "status": "integration-error",
            }
            _write(
                document=document,
                lines=("ERROR replay physical replay ended without a typed result",),
                json_mode=json_mode,
                error=True,
            )
            return _ExitCode.INTEGRATION
        document = {
            "representation": {
                "accepted": False,
                "result_code": representation.result_code,
                "stage": representation.stage,
            },
            "status": "representation-rejected",
        }
        _write(
            document=document,
            lines=(
                "FAIL replay representation-rejected "
                f"stage={representation.stage} "
                f"result={representation.result_code}",
            ),
            json_mode=json_mode,
        )
        return _ExitCode.REJECTED

    report_document = replay_report_to_json_object(report=execution.report)
    package_identifier = report_document.get("packageIdentifier") or "-"
    derived_verdict = report_document.get("derivedVerdict", "-")
    status = str(report_document["status"])
    label = "OK" if execution.successful else "FAIL"
    _write(
        document=report_document,
        lines=(
            f"{label} replay status={status} derived-verdict={derived_verdict}",
            f"  package={package_identifier}",
        ),
        json_mode=json_mode,
    )
    return _ExitCode.SUCCESS if execution.successful else _ExitCode.REJECTED


def _run_conformance(*, json_mode: bool) -> int:
    from belgi.replay.conformance.installed.document import (
        installed_conformance_to_json_object,
    )
    from belgi.replay.conformance.installed.suite import (
        run_installed_conformance_suite,
    )

    try:
        suite = run_installed_conformance_suite()
    except Exception as exc:
        document = {
            "detail": str(exc),
            "error_type": type(exc).__name__,
            "status": "integration-error",
            "successful": False,
        }
        _write(
            document=document,
            lines=(f"ERROR conformance {exc}",),
            json_mode=json_mode,
            error=True,
        )
        return _ExitCode.INTEGRATION
    document = installed_conformance_to_json_object(suite=suite)
    label = "OK" if suite.successful else "FAIL"
    lines = [
        f"{label} conformance normative={len(suite.normative_corpora)} "
        f"implementation-checks={len(suite.implementation_checks)}"
    ]
    lines.extend(
        f"  normative {result.role} "
        f"cases={result.executed_case_count}/{result.source_case_count} "
        f"mismatches={result.mismatch_count}"
        for result in suite.normative_corpora
    )
    lines.extend(
        f"  implementation-check {result.check_id} "
        f"cases={result.executed_case_count}/{result.source_case_count} "
        f"problems={result.problem_count}"
        for result in suite.implementation_checks
    )
    _write(document=document, lines=lines, json_mode=json_mode)
    return _ExitCode.SUCCESS if suite.successful else _ExitCode.REJECTED


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = tuple(sys.argv[1:] if argv is None else argv)
    json_requested = _root_json_requested(raw_argv)
    parser = _parser()
    try:
        namespace = parser.parse_args(raw_argv)
    except _UsageError as exc:
        document = {
            "detail": str(exc),
            "status": "usage-error",
            "usage": parser.format_usage().strip(),
        }
        _write(
            document=document,
            lines=(f"ERROR {exc}", parser.format_usage().strip()),
            json_mode=json_requested,
            error=True,
        )
        return _ExitCode.USAGE

    if namespace.command == "replay":
        return _run_replay(
            package_path=Path(namespace.path),
            json_mode=bool(namespace.json_mode),
        )
    if namespace.command == "conformance":
        return _run_conformance(json_mode=bool(namespace.json_mode))
    raise RuntimeError(f"unsupported command dispatch: {namespace.command!r}")


__all__ = ["main"]
