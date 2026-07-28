from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from belgi.carrier import CanonicalReference
from belgi.cli import main
from belgi.replay.lifting.exceptions import ResolveFailureError
from belgi.replay.reference_profile.judged.generic_source_state import (
    require_generic_source_state_records,
)

from .conftest import run_belgi, stdout_json

_FORBIDDEN_CONFORMANCE_IMPORT_MARKERS = (
    "belgi.product",
    ".operational_action",
    ".console",
    ".mcp",
    ".gateway",
    ".terraform",
    ".aws",
    ".opa",
    "carrier.integrity.signing",
    "carrier.package.assembly",
    "carrier.package.emission",
    "finite_evaluator.conformance.signed_witness",
    "replay.conformance.api",
    "replay.reference_profile.conformance",
    "replay.report_conformance",
    "substrate.subprocess",
    "substrate.yaml",
)
_CONFORMANCE_SOURCE_STATE_MODULES = frozenset(
    {
        "belgi.profile.reference_profile.judged.source_state",
        "belgi.replay.reference_profile.judged.generic_source_state",
        "belgi.replay.reference_profile.judged.part4_source_state",
        "belgi.replay.reference_profile.judged.source_state",
    }
)


def test_help_exposes_only_public_commands(repository_root: Path) -> None:
    process = run_belgi("--help", cwd=repository_root)

    assert process.returncode == 0
    assert "{replay,conformance}" in process.stdout
    for excluded_command in (
        "agent-session",
        "console",
        "doctor",
        "enforce",
        "experimental",
        "export",
        "init",
        "mcp",
        "verify",
    ):
        assert excluded_command not in process.stdout


@pytest.mark.parametrize("command", ("run", "verify", "experimental", "mcp"))
def test_legacy_commands_are_usage_errors(
    repository_root: Path,
    command: str,
) -> None:
    process = run_belgi("--json", command, cwd=repository_root)

    assert process.returncode == 2
    assert stdout_json(process)["status"] == "usage-error"
    assert "Traceback" not in process.stderr


def test_static_directory_examples_prove_success_and_pre_lifting_tamper(
    repository_root: Path,
) -> None:
    positive = run_belgi(
        "--json",
        "replay",
        "examples/finite-review-record",
        cwd=repository_root,
    )
    tampered = run_belgi(
        "--json",
        "replay",
        "examples/finite-review-record-tampered",
        cwd=repository_root,
    )

    assert positive.returncode == 0
    assert stdout_json(positive)["outcomeClass"] == "successful-replay"
    assert tampered.returncode == 1
    tampered_document = stdout_json(tampered)
    assert tampered_document["outcomeClass"] == "integrity-failure"
    assert [
        problem["type"]
        for problem in tampered_document["problems"]  # type: ignore[index]
    ] == ["integrity-binding-mismatch"]
    assert "Traceback" not in tampered.stderr


def test_static_pair_is_the_finite_part_4_record_and_one_byte_tamper(
    repository_root: Path,
) -> None:
    positive = repository_root / "examples" / "finite-review-record"
    tampered = repository_root / "examples" / "finite-review-record-tampered"
    positive_members = {
        member.name: member.read_bytes()
        for member in positive.iterdir()
        if member.is_file()
    }
    tampered_members = {
        member.name: member.read_bytes()
        for member in tampered.iterdir()
        if member.is_file()
    }

    assert positive_members.keys() == tampered_members.keys()
    evaluator = json.loads(positive_members["evaluator-carrier-root"])
    assert evaluator["replayPolicy"] == "belgi.software-change.replay.record-check"
    assert set(evaluator["declaredConditions"]) == {
        "belgi.software-change.condition.change-basis-resolved",
        "belgi.software-change.condition.required-evidence-present",
        "belgi.software-change.condition.review-policy-satisfied",
    }
    differences = [
        (name, offset, left, right)
        for name, positive_bytes in positive_members.items()
        for offset, (left, right) in enumerate(
            zip(positive_bytes, tampered_members[name], strict=True)
        )
        if left != right
    ]
    assert differences == [("proposed-source-state", 75, 0x65, 0x75)]


def test_missing_path_is_an_integration_error(repository_root: Path) -> None:
    process = run_belgi(
        "--json",
        "replay",
        "examples/does-not-exist",
        cwd=repository_root,
    )

    assert process.returncode == 3
    assert stdout_json(process)["status"] == "io-error"
    assert "Traceback" not in process.stderr


def test_conformance_separates_normative_corpora_from_implementation_checks(
    capsys: pytest.CaptureFixture[str],
) -> None:
    return_code = main(["--json", "conformance"])
    captured = capsys.readouterr()

    assert return_code == 0
    document = json.loads(captured.out)
    assert document["status"] == "passed"
    assert [
        result["role"]
        for result in document["normative_corpora"]  # type: ignore[index]
    ] == [
        "json-representation",
        "replay-package-representation",
        "package-integrity-crypto",
    ]
    implementation_checks = document["implementation_checks"]
    assert [
        (result["check_id"], result["classification"], result["scope"])
        for result in implementation_checks  # type: ignore[union-attr]
    ] == [
        (
            "software-change-finite-reference-validation",
            "implementation_check",
            "finite-reference-validation",
        )
    ]


def test_conformance_import_closure_uses_no_private_or_git_process_modules(
    repository_root: Path,
) -> None:
    script = f"""
import contextlib
import io
import json
import sys
from belgi.cli import main

output = io.StringIO()
with contextlib.redirect_stdout(output):
    return_code = main(["--json", "conformance"])
document = json.loads(output.getvalue())
markers = {_FORBIDDEN_CONFORMANCE_IMPORT_MARKERS!r}
loaded = sorted(name for name in sys.modules if name.startswith("belgi"))
source_state_modules = sorted(
    name
    for name in loaded
    if name.endswith(("source_state", "source_state_extension"))
)
allowed_git_modules = {{
    "belgi.substrate.git",
    "belgi.substrate.git.identity",
}}
forbidden = [
    name
    for name in loaded
    if (
        (
            name == "belgi.substrate.git"
            or name.startswith("belgi.substrate.git.")
        )
        and name not in allowed_git_modules
    )
    or any(marker in name for marker in markers)
]
print(json.dumps({{
    "return_code": int(return_code),
    "status": document["status"],
    "forbidden": forbidden,
    "source_state_modules": source_state_modules,
}}))
"""
    process = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    report = json.loads(process.stdout)
    assert report == {
        "return_code": 0,
        "status": "passed",
        "forbidden": [],
        "source_state_modules": sorted(_CONFORMANCE_SOURCE_STATE_MODULES),
    }


def test_generic_part4_records_reject_extension_fields() -> None:
    with pytest.raises(ResolveFailureError):
        require_generic_source_state_records(
            proposal={
                "identifier": "proposal:generic",
                "source_state": "source-state:proposal",
                "unexpected": "extension-field",
            },
            baseline={
                "identifier": "baseline:generic",
                "source_state": "source-state:baseline",
            },
            root_reference=CanonicalReference("pkg:generic#judged-object"),
        )


def test_json_output_rejects_non_finite_numbers(
    repository_root: Path,
) -> None:
    script = """
from belgi.cli import _write

try:
    _write(document={"value": float("nan")}, lines=(), json_mode=True)
except ValueError as error:
    assert "Out of range float values" in str(error)
else:
    raise AssertionError("non-finite JSON output was accepted")
print("NON_FINITE_JSON_REJECTED")
"""
    process = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    assert process.stdout == "NON_FINITE_JSON_REJECTED\n"
    assert process.stderr == ""


@pytest.mark.skipif(os.name == "nt", reason="POSIX filesystem-kind witness")
def test_symlink_and_fifo_paths_are_rejected_as_unsupported_kinds(
    repository_root: Path,
    tmp_path: Path,
) -> None:
    symlink = tmp_path / "package-link"
    symlink.symlink_to(repository_root / "examples" / "finite-review-record")
    fifo = tmp_path / "package-fifo"
    os.mkfifo(fifo)

    for path in (symlink, fifo):
        process = run_belgi(
            "--json",
            "replay",
            str(path),
            cwd=repository_root,
        )
        assert process.returncode == 2
        assert stdout_json(process)["status"] == "unsupported-path-kind"
        assert "Traceback" not in process.stderr
