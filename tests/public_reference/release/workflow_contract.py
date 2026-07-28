from __future__ import annotations

from pathlib import Path

import yaml

PUBLISH_ACTION = "pypa/gh-action-pypi-publish@ba38be9e461d3875417946c167d0b5f3d385a247"


def assert_step_fails_closed(step: dict[str, object]) -> None:
    assert "continue-on-error" not in step


def workflow(repository_root: Path) -> dict[str, object]:
    document = yaml.load(
        (repository_root / ".github/workflows/publish.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert isinstance(document, dict)
    return document


def jobs(document: dict[str, object]) -> dict[str, dict[str, object]]:
    job_documents = document["jobs"]
    assert isinstance(job_documents, dict)
    assert all(isinstance(job, dict) for job in job_documents.values())
    return job_documents  # type: ignore[return-value]


def steps(job: dict[str, object]) -> list[dict[str, object]]:
    step_documents = job["steps"]
    assert isinstance(step_documents, list)
    assert all(isinstance(step, dict) for step in step_documents)
    return step_documents  # type: ignore[return-value]


def run_text(job: dict[str, object]) -> str:
    return "\n".join(str(step["run"]) for step in steps(job) if "run" in step)


def normalized_run_lines(text: str) -> tuple[str, ...]:
    return tuple(line.strip() for line in text.strip().splitlines())


def named_step(job: dict[str, object], name: str) -> dict[str, object]:
    matches = [step for step in steps(job) if step.get("name") == name]
    assert len(matches) == 1
    return matches[0]


def step_index(job: dict[str, object], name: str) -> int:
    step_documents = steps(job)
    return step_documents.index(named_step(job, name))
