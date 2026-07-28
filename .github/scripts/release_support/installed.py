from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from release_support.common import ReleaseArtifactError, require

_FORBIDDEN_PREFIXES = (
    "belgi.product",
    "belgi.carrier.integrity.signing",
    "belgi.carrier.package.assembly",
    "belgi.carrier.package.emission",
    "belgi.replay.reference_profile.finite_evaluator.conformance.signed_witness",
    "belgi.substrate.git",
    "belgi.substrate.subprocess",
    "belgi.substrate.yaml",
)
_FORBIDDEN_FRAGMENTS = (
    ".operational_action",
    ".console",
    ".mcp",
    ".gateway",
    ".terraform",
    ".aws",
    ".opa",
)
_ALLOWED_MODULES = {
    "belgi.substrate.git",
    "belgi.substrate.git.identity",
}


def _run_json(
    arguments: Sequence[str],
    *,
    expected_status: int,
    cwd: Path,
) -> dict[str, Any]:
    process = subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        cwd=cwd,
        text=True,
    )
    require(
        process.returncode == expected_status,
        f"command returned {process.returncode}, expected {expected_status}: "
        f"{' '.join(arguments)}\n{process.stderr}",
    )
    try:
        document = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise ReleaseArtifactError(
            f"command emitted non-JSON output: {' '.join(arguments)}"
        ) from error
    require(isinstance(document, dict), "command JSON result is not an object")
    return document


def _installed_prefix(
    *,
    environment: Path,
    python: Path,
    expected_version: str,
) -> Path:
    prefix_document = _run_json(
        [
            str(python),
            "-c",
            (
                "import json, sys, belgi; "
                "print(json.dumps({"
                "'exports': belgi.__all__, "
                "'module': belgi.__file__, "
                "'prefix': sys.prefix, "
                "'version': belgi.__version__"
                "}))"
            ),
        ],
        expected_status=0,
        cwd=environment,
    )
    prefix_value = prefix_document.get("prefix")
    module_value = prefix_document.get("module")
    require(
        isinstance(prefix_value, str),
        "installed package identity result has no prefix",
    )
    require(
        prefix_document.get("exports") == ["__version__"],
        "installed package export surface mismatch",
    )
    require(
        prefix_document.get("version") == expected_version,
        "installed package version mismatch",
    )
    require(
        isinstance(module_value, str),
        "installed package identity result has no module path",
    )
    prefix_value = cast(str, prefix_value)
    module_value = cast(str, module_value)
    environment_prefix = Path(prefix_value)
    require(
        environment_prefix.resolve(strict=True) == environment.resolve(strict=True),
        "installed package reported an unexpected environment prefix",
    )
    require(
        Path(module_value)
        .resolve(strict=True)
        .is_relative_to(environment_prefix.resolve(strict=True)),
        "installed package was shadowed outside the environment",
    )
    return environment_prefix


def verify_installed_journey(
    *,
    environment: Path,
    expected_version: str,
) -> None:
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    cli = scripts / ("belgi.exe" if os.name == "nt" else "belgi")
    require(python.is_file(), f"installed Python is missing: {python}")
    require(cli.is_file(), f"installed CLI is missing: {cli}")
    environment_prefix = _installed_prefix(
        environment=environment,
        python=python,
        expected_version=expected_version,
    )
    examples = environment_prefix / "share" / "belgi" / "examples"
    help_result = subprocess.run(
        [str(cli), "--help"],
        check=False,
        capture_output=True,
        cwd=environment,
        text=True,
    )
    require(
        help_result.returncode == 0 and "{replay,conformance}" in help_result.stdout,
        "installed command surface mismatch",
    )

    positive = _run_json(
        [
            str(cli),
            "--json",
            "replay",
            str(examples / "finite-review-record"),
        ],
        expected_status=0,
        cwd=environment,
    )
    require(
        (
            positive.get("status"),
            positive.get("outcomeClass"),
            positive.get("derivedVerdict"),
        )
        == ("replayable", "successful-replay", 1),
        "installed positive replay result mismatch",
    )
    tampered = _run_json(
        [
            str(cli),
            "--json",
            "replay",
            str(examples / "finite-review-record-tampered"),
        ],
        expected_status=1,
        cwd=environment,
    )
    require(
        tampered.get("outcomeClass") == "integrity-failure"
        and [
            problem.get("type")
            for problem in tampered.get("problems", [])
            if isinstance(problem, dict)
        ]
        == ["integrity-binding-mismatch"],
        "installed tamper rejection result mismatch",
    )
    conformance = _run_json(
        [str(cli), "--json", "conformance"],
        expected_status=0,
        cwd=environment,
    )
    require(
        conformance.get("status") == "passed",
        "installed conformance did not pass",
    )
    closure_script = f"""
import contextlib
import io
import json
import sys
from belgi.cli import main

with contextlib.redirect_stdout(io.StringIO()):
    replay_status = main(["--json", "replay", sys.argv[1]])
    conformance_status = main(["--json", "conformance"])
if (replay_status, conformance_status) != (0, 0):
    raise SystemExit(
        f"installed import census journeys failed: "
        f"replay={{replay_status}}, conformance={{conformance_status}}"
    )

prefixes = {_FORBIDDEN_PREFIXES!r}
fragments = {_FORBIDDEN_FRAGMENTS!r}
allowed = {_ALLOWED_MODULES!r}
forbidden = sorted(
    name
    for name in sys.modules
    if name not in allowed
    and (
        any(name == prefix or name.startswith(prefix + ".") for prefix in prefixes)
        or any(fragment in name for fragment in fragments)
    )
)
print(json.dumps({{"forbidden": forbidden}}))
"""
    closure = subprocess.run(
        [
            str(python),
            "-c",
            closure_script,
            str(examples / "finite-review-record"),
        ],
        check=False,
        capture_output=True,
        cwd=environment,
        text=True,
    )
    require(
        closure.returncode == 0, f"installed import census failed: {closure.stderr}"
    )
    require(
        json.loads(closure.stdout) == {"forbidden": []},
        "installed import closure contains excluded modules",
    )
