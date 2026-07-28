from __future__ import annotations

import re
from pathlib import Path

import pytest

from .workflow_contract import (
    PUBLISH_ACTION,
    assert_step_fails_closed,
    jobs,
    named_step,
    normalized_run_lines,
    run_text,
    step_index,
    steps,
    workflow,
)

_ACTION_PIN = re.compile(r"^[^@]+@[0-9a-f]{40}$")
_REBIND_STEP_NAME = "Rebind the remote annotated tag"
_REBIND_COMMAND_LINES = (
    'test "$(',
    "sha256sum workflow-support/release_tag.py",
    ')" = "${RELEASE_TAG_SHA256}  workflow-support/release_tag.py"',
    "python3 workflow-support/release_tag.py \\",
    '--repository "https://github.com/${GITHUB_REPOSITORY}.git" \\',
    '--tag "${RELEASE_TAG}" \\',
    '--tag-object "${RELEASE_TAG_OBJECT}" \\',
    '--commit "${RELEASE_COMMIT}"',
)
_CANDIDATE_DIGEST_COMMAND_LINES = (
    'test "$(',
    "sha256sum evidence/SHA256SUMS",
    ')" = "${CHECKSUMS_SHA256}  evidence/SHA256SUMS"',
    'test "$(',
    "sha256sum evidence/release-evidence.json",
    ')" = "${EVIDENCE_SHA256}  evidence/release-evidence.json"',
    "sha256sum --check evidence/SHA256SUMS",
)


def _assert_remote_tag_rebind(text: str) -> None:
    assert normalized_run_lines(text) == _REBIND_COMMAND_LINES


def _assert_candidate_digest_binding(text: str) -> None:
    assert normalized_run_lines(text) == _CANDIDATE_DIGEST_COMMAND_LINES


def test_release_boundary_helper_is_a_separate_digest_bound_artifact(
    repository_root: Path,
) -> None:
    build = jobs(workflow(repository_root))["build"]
    binding = named_step(build, "Bind the release boundary helper")
    text = str(binding["run"])
    assert "cp .github/scripts/release_tag.py workflow-support/release_tag.py" in text
    assert "sha256sum workflow-support/release_tag.py" in text
    assert "printf 'sha256=%s\\n'" in text
    upload = named_step(build, "Upload the bound release helper")
    assert upload["with"] == {
        "name": "release-workflow-support",
        "path": "workflow-support/",
        "if-no-files-found": "error",
        "retention-days": "90",
    }


def test_publish_jobs_bind_candidate_to_build_outputs_before_upload(
    repository_root: Path,
) -> None:
    workflow_jobs = jobs(workflow(repository_root))

    for name in ("testpypi", "pypi"):
        job = workflow_jobs[name]
        assert job["env"] == {
            "CHECKSUMS_SHA256": "${{ needs.build.outputs.checksums_sha256 }}",
            "EVIDENCE_SHA256": "${{ needs.build.outputs.evidence_sha256 }}",
            "RELEASE_COMMIT": "${{ needs.build.outputs.commit }}",
            "RELEASE_TAG": "${{ needs.build.outputs.tag }}",
            "RELEASE_TAG_OBJECT": "${{ needs.build.outputs.tag_object }}",
            "RELEASE_TAG_SHA256": "${{ needs.build.outputs.release_tag_sha256 }}",
        }
        digest_step = named_step(job, "Verify downloaded candidate digests")
        assert_step_fails_closed(digest_step)
        _assert_candidate_digest_binding(str(digest_step["run"]))
        download_steps = [
            step
            for step in steps(job)
            if str(step.get("uses", "")).startswith("actions/download-artifact@")
        ]
        assert {
            (step["with"]["name"], step["with"]["path"])  # type: ignore[index]
            for step in download_steps
        } == {
            ("release-candidate", "candidate"),
            ("release-workflow-support", "workflow-support"),
        }
        publish_steps = [
            step for step in steps(job) if step.get("uses") == PUBLISH_ACTION
        ]
        assert len(publish_steps) == 1
        options = publish_steps[0]["with"]
        assert isinstance(options, dict)
        assert options["packages-dir"] == "candidate/dist"
        assert "skip-existing" not in options


@pytest.mark.parametrize(
    ("job_name", "irreversible_step"),
    (
        ("testpypi", "Publish to TestPyPI"),
        ("pypi", "Publish to PyPI"),
        ("github-release", "Create the prerelease from admitted and read-back bytes"),
    ),
)
def test_irreversible_jobs_rebind_the_remote_tag_at_the_boundary(
    repository_root: Path,
    job_name: str,
    irreversible_step: str,
) -> None:
    job = jobs(workflow(repository_root))[job_name]
    environment = job["env"]
    assert isinstance(environment, dict)
    assert environment["RELEASE_COMMIT"] == "${{ needs.build.outputs.commit }}"
    assert environment["RELEASE_TAG"] == "${{ needs.build.outputs.tag }}"
    assert environment["RELEASE_TAG_OBJECT"] == (
        "${{ needs.build.outputs.tag_object }}"
    )
    assert environment["RELEASE_TAG_SHA256"] == (
        "${{ needs.build.outputs.release_tag_sha256 }}"
    )
    rebind = named_step(job, _REBIND_STEP_NAME)
    assert_step_fails_closed(rebind)
    _assert_remote_tag_rebind(str(rebind["run"]))
    assert step_index(job, _REBIND_STEP_NAME) + 1 == step_index(
        job,
        irreversible_step,
    )


def test_remote_tag_rebind_is_one_exact_contract(
    repository_root: Path,
) -> None:
    workflow_jobs = jobs(workflow(repository_root))
    bodies = {
        str(named_step(workflow_jobs[name], _REBIND_STEP_NAME)["run"])
        for name in ("testpypi", "pypi", "github-release")
    }

    assert len(bodies) == 1


@pytest.mark.parametrize(
    ("old", "new"),
    (
        (
            ')" = "${RELEASE_TAG_SHA256}  workflow-support/release_tag.py"',
            ')" = "${RELEASE_TAG_SHA256}  workflow-support/release_tag.py" || true',
        ),
        (
            '--commit "${RELEASE_COMMIT}"',
            '--commit "${RELEASE_COMMIT}" || true',
        ),
        (
            '--tag-object "${RELEASE_TAG_OBJECT}" \\',
            "",
        ),
    ),
)
def test_remote_tag_rebind_contract_rejects_non_failing_or_missing_edges(
    repository_root: Path,
    old: str,
    new: str,
) -> None:
    job = jobs(workflow(repository_root))["testpypi"]
    text = str(named_step(job, _REBIND_STEP_NAME)["run"])
    mutated = text.replace(old, new, 1)

    with pytest.raises(AssertionError):
        _assert_remote_tag_rebind(mutated)


@pytest.mark.parametrize(
    ("old", "new"),
    (
        (
            ')" = "${CHECKSUMS_SHA256}  evidence/SHA256SUMS"',
            ')" = "${CHECKSUMS_SHA256}  evidence/SHA256SUMS" || true',
        ),
        (
            "sha256sum --check evidence/SHA256SUMS",
            "sha256sum --check evidence/SHA256SUMS || true",
        ),
        (
            "sha256sum evidence/release-evidence.json",
            "",
        ),
    ),
)
def test_candidate_digest_contract_rejects_non_failing_or_missing_edges(
    repository_root: Path,
    old: str,
    new: str,
) -> None:
    job = jobs(workflow(repository_root))["testpypi"]
    text = str(named_step(job, "Verify downloaded candidate digests")["run"])
    mutated = text.replace(old, new, 1)

    with pytest.raises(AssertionError):
        _assert_candidate_digest_binding(mutated)


@pytest.mark.parametrize(
    ("job_name", "step_name"),
    (
        ("testpypi", "Verify downloaded candidate digests"),
        ("testpypi", _REBIND_STEP_NAME),
        ("pypi", "Verify downloaded candidate digests"),
        ("pypi", _REBIND_STEP_NAME),
        ("github-release", "Verify downloaded candidate digests"),
        ("github-release", _REBIND_STEP_NAME),
    ),
)
def test_irreversible_boundary_guards_reject_continue_on_error(
    repository_root: Path,
    job_name: str,
    step_name: str,
) -> None:
    job = jobs(workflow(repository_root))[job_name]
    mutated = {**named_step(job, step_name), "continue-on-error": "true"}

    with pytest.raises(AssertionError):
        assert_step_fails_closed(mutated)


def test_publish_workflow_separates_oidc_and_orders_readback(
    repository_root: Path,
) -> None:
    workflow_jobs = jobs(workflow(repository_root))

    for name, environment in (("testpypi", "testpypi"), ("pypi", "pypi")):
        job = workflow_jobs[name]
        assert job["permissions"] == {"id-token": "write"}
        assert job["environment"]["name"] == environment  # type: ignore[index]
        assert PUBLISH_ACTION in {step.get("uses") for step in steps(job)}
    for name, job in workflow_jobs.items():
        if name not in {"testpypi", "pypi"}:
            assert "id-token" not in job.get("permissions", {})

    assert set(workflow_jobs["testpypi-readback"]["needs"]) == {
        "build",
        "testpypi",
    }
    assert set(workflow_jobs["pypi"]["needs"]) == {
        "build",
        "testpypi-readback",
    }
    assert set(workflow_jobs["pypi-readback"]["needs"]) == {"build", "pypi"}
    assert set(workflow_jobs["github-release"]["needs"]) == {
        "build",
        "pypi-readback",
    }
    github_release = workflow_jobs["github-release"]
    assert github_release["permissions"] == {"contents": "write"}
    assert github_release["env"]["GH_REPO"] == "${{ github.repository }}"  # type: ignore[index]
    assert github_release["env"]["CHECKSUMS_SHA256"] == (  # type: ignore[index]
        "${{ needs.build.outputs.checksums_sha256 }}"
    )
    assert github_release["env"]["EVIDENCE_SHA256"] == (  # type: ignore[index]
        "${{ needs.build.outputs.evidence_sha256 }}"
    )
    assert github_release["env"]["RELEASE_TAG_SHA256"] == (  # type: ignore[index]
        "${{ needs.build.outputs.release_tag_sha256 }}"
    )
    _assert_candidate_digest_binding(
        str(named_step(github_release, "Verify downloaded candidate digests")["run"])
    )
    github_release_text = run_text(github_release)
    assert "gh release create" in github_release_text
    assert "--prerelease" in github_release_text


def test_index_jobs_verify_candidate_before_readback(
    repository_root: Path,
) -> None:
    workflow_jobs = jobs(workflow(repository_root))
    for name in ("testpypi-readback", "pypi-readback"):
        job = workflow_jobs[name]
        environment = job["env"]
        assert isinstance(environment, dict)
        assert environment["RELEASE_TAG_OBJECT"] == (
            "${{ needs.build.outputs.tag_object }}"
        )
        text = run_text(job)
        assert '--tag-object "${RELEASE_TAG_OBJECT}"' in text
        assert text.index("release_artifacts.py verify") < text.index(
            "release_artifacts.py readback"
        )


def test_every_external_action_is_immutably_pinned(
    repository_root: Path,
) -> None:
    uses = [
        str(step["uses"])
        for job in jobs(workflow(repository_root)).values()
        for step in steps(job)
        if "uses" in step
    ]

    assert uses
    assert all(_ACTION_PIN.fullmatch(item) is not None for item in uses)
    assert uses.count(PUBLISH_ACTION) == 2
