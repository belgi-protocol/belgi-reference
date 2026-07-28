from __future__ import annotations

from pathlib import Path

import pytest

from .workflow_contract import (
    assert_step_fails_closed,
    jobs,
    named_step,
    run_text,
    step_index,
    steps,
    workflow,
)

_IDENTITY_GUARDS = (
    'test "${GITHUB_REF}" = "refs/heads/main"',
    'tag_ref="refs/tags/${RELEASE_TAG}"',
    'git rev-parse --verify --end-of-options "${tag_ref}^{tag}" >/dev/null',
    'tag_object="$(git rev-parse --verify --end-of-options "${tag_ref}^{tag}")"',
    'commit="$(git rev-parse --verify --end-of-options "${tag_ref}^{commit}")"',
    'tree="$(git rev-parse --verify --end-of-options "${tag_ref}^{tree}")"',
    'main_commit="$(git rev-parse refs/remotes/origin/main)"',
    'test "${GITHUB_SHA}" = "${main_commit}"',
    'test "${commit}" = "${main_commit}"',
    'test "$(git rev-parse HEAD)" = "${commit}"',
)


def _assert_identity_guards_are_direct_commands(text: str) -> None:
    lines = {line.strip() for line in text.splitlines()}
    assert set(_IDENTITY_GUARDS) <= lines


def _assert_bootstrap_step_order(build: dict[str, object]) -> None:
    build_steps = steps(build)
    checkout = build_steps[0]
    assert str(checkout["uses"]).startswith("actions/checkout@")
    assert checkout["with"]["ref"] == "${{ github.sha }}"  # type: ignore[index]
    assert "${{ inputs.release_tag }}" not in str(checkout["with"])  # type: ignore[index]

    identity_index = step_index(
        build,
        "Bind main dispatch, annotated tag, and confirmation",
    )
    archive_index = step_index(
        build,
        "Materialize and compare the exact tagged archive",
    )
    setup_index = step_index(build, "Set up Python 3.11")
    install_index = step_index(build, "Install release tools")
    assert identity_index == 1
    assert archive_index == 2
    assert archive_index < setup_index < install_index
    assert_step_fails_closed(
        named_step(build, "Bind main dispatch, annotated tag, and confirmation")
    )
    assert_step_fails_closed(
        named_step(build, "Materialize and compare the exact tagged archive")
    )


def test_publish_workflow_requires_one_explicit_dispatch(
    repository_root: Path,
) -> None:
    document = workflow(repository_root)
    trigger = document["on"]
    assert isinstance(trigger, dict)
    assert set(trigger) == {"workflow_dispatch"}
    dispatch = trigger["workflow_dispatch"]
    assert isinstance(dispatch, dict)
    inputs = dispatch["inputs"]
    assert isinstance(inputs, dict)
    assert set(inputs) == {"release_tag", "confirmation"}
    assert document["permissions"] == {}

    build = jobs(document)["build"]
    text = run_text(build)
    _assert_identity_guards_are_direct_commands(text)
    assert '"refs/tags/${RELEASE_TAG}"' in text
    assert '"${RELEASE_TAG}^{tag}"' not in text
    assert 'test "${RELEASE_TAG}" = "v${version}"' in text
    assert (
        'test "${RELEASE_CONFIRMATION}" = '
        '"publish belgi==${version} from ${RELEASE_TAG}"'
    ) in text
    assert "release_artifacts.py materialize-source" in text
    assert '--archive "${RUNNER_TEMP}/tag-source.tar"' in text
    assert '--destination "${RUNNER_TEMP}/tag-source"' in text


def test_build_binds_main_and_tag_before_tag_controlled_execution(
    repository_root: Path,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    _assert_bootstrap_step_order(build)


def test_build_rejects_execution_between_checkout_and_identity_binding(
    repository_root: Path,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    build_steps = steps(build)
    mutated = {
        **build,
        "steps": [
            build_steps[0],
            {"name": "Run tag-controlled code", "run": "python -V"},
            *build_steps[1:],
        ],
    }

    with pytest.raises(AssertionError):
        _assert_bootstrap_step_order(mutated)


@pytest.mark.parametrize(
    "step_name",
    (
        "Bind main dispatch, annotated tag, and confirmation",
        "Materialize and compare the exact tagged archive",
    ),
)
def test_bootstrap_steps_reject_continue_on_error(
    repository_root: Path,
    step_name: str,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    mutated = {**named_step(build, step_name), "continue-on-error": "true"}

    with pytest.raises(AssertionError):
        assert_step_fails_closed(mutated)


@pytest.mark.parametrize("guard", _IDENTITY_GUARDS)
def test_identity_guard_contract_rejects_non_failing_shell_variants(
    repository_root: Path,
    guard: str,
) -> None:
    text = run_text(jobs(workflow(repository_root))["build"])
    mutated = text.replace(guard, f"{guard} || true", 1)

    with pytest.raises(AssertionError):
        _assert_identity_guards_are_direct_commands(mutated)


def test_publish_workflow_builds_and_admits_once(
    repository_root: Path,
) -> None:
    workflow_jobs = jobs(workflow(repository_root))
    build_text = run_text(workflow_jobs["build"])
    non_build_text = "\n".join(
        run_text(job) for name, job in workflow_jobs.items() if name != "build"
    )

    assert build_text.count("python -m build") == 2
    assert "--sdist" in build_text
    assert "for build_name in first second" in build_text
    assert "--first-wheel-directory" in build_text
    assert "--second-wheel-directory" in build_text
    assert "python -m twine check candidate/dist/*" in build_text
    assert "tests/public_reference" in build_text
    assert "release_artifacts.py installed" in build_text
    build_outputs = workflow_jobs["build"]["outputs"]
    assert isinstance(build_outputs, dict)
    assert build_outputs["checksums_sha256"] == (
        "${{ steps.candidate.outputs.checksums_sha256 }}"
    )
    assert build_outputs["evidence_sha256"] == (
        "${{ steps.candidate.outputs.evidence_sha256 }}"
    )
    assert build_outputs["tag_object"] == "${{ steps.identity.outputs.tag_object }}"
    assert build_outputs["release_tag_sha256"] == (
        "${{ steps.release-support.outputs.sha256 }}"
    )
    assert "python -m build" not in non_build_text
