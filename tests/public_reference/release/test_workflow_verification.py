from __future__ import annotations

import re
from pathlib import Path

import pytest

from .workflow_contract import (
    assert_step_fails_closed,
    jobs,
    named_step,
    normalized_run_lines,
    workflow,
)

_TYPING_ISOLATION_LINES = (
    "(",
    'cd "${typing_root}"',
    "python -m pyright \\",
    '--pythonpath "${environment}/bin/python" \\',
    "typing_consumer.py",
    ")",
)


def _assert_typing_isolation(text: str) -> None:
    lines = normalized_run_lines(text)
    start = lines.index("(")
    assert lines[start : start + len(_TYPING_ISOLATION_LINES)] == (
        _TYPING_ISOLATION_LINES
    )


def test_installed_typing_check_excludes_the_checkout_from_resolution(
    repository_root: Path,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    typing_step = named_step(
        build,
        "Verify the installed release journey and typing marker",
    )
    assert_step_fails_closed(typing_step)
    text = str(typing_step["run"])

    assert 'typing_root="${RUNNER_TEMP}/typing-check"' in text
    _assert_typing_isolation(text)
    assert '"${RUNNER_TEMP}/typing_consumer.py"' not in text


@pytest.mark.parametrize(
    ("old", "new"),
    (
        (
            '  cd "${typing_root}"\n  python -m pyright',
            "  python -m pyright",
        ),
        (
            '  cd "${typing_root}"\n  python -m pyright',
            '  python -m pyright\n  cd "${typing_root}"',
        ),
        (
            "    typing_consumer.py\n)",
            "    typing_consumer.py || true\n)",
        ),
    ),
)
def test_installed_typing_contract_rejects_dead_or_non_failing_isolation(
    repository_root: Path,
    old: str,
    new: str,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    text = str(
        named_step(build, "Verify the installed release journey and typing marker")[
            "run"
        ]
    )
    mutated = text.replace(old, new, 1)

    with pytest.raises((AssertionError, ValueError)):
        _assert_typing_isolation(mutated)


def test_installed_typing_step_rejects_continue_on_error(
    repository_root: Path,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    step = named_step(
        build,
        "Verify the installed release journey and typing marker",
    )
    mutated = {**step, "continue-on-error": "true"}

    with pytest.raises(AssertionError):
        assert_step_fails_closed(mutated)


def test_verify_workflow_uses_the_release_helper_as_installed_owner(
    repository_root: Path,
) -> None:
    text = (repository_root / ".github/workflows/verify.yml").read_text(
        encoding="utf-8"
    )

    assert "release_artifacts.py installed" in text
    assert "forbidden_prefixes =" not in text
    assert "tests/public_reference" in text
    assert ".github/scripts" in text


def test_release_execution_surfaces_do_not_use_optimizable_assertions(
    repository_root: Path,
) -> None:
    execution_paths = [
        repository_root / ".github/workflows/publish.yml",
        repository_root / ".github/workflows/verify.yml",
        *sorted((repository_root / ".github/scripts").rglob("*.py")),
    ]

    assert not {
        path.relative_to(repository_root).as_posix()
        for path in execution_paths
        if re.search(r"(?m)^\s*assert\s", path.read_text(encoding="utf-8"))
    }
