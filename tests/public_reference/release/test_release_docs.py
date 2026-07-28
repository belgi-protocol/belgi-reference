from __future__ import annotations

import tomllib
from pathlib import Path


def test_repository_and_package_readmes_are_one_owned_projection(
    repository_root: Path,
) -> None:
    readme = (repository_root / "README.md").read_bytes()
    package_readme = (repository_root / "PACKAGE_README.md").read_bytes()
    project = tomllib.loads(
        (repository_root / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    index_install = (
        f'python -m pip install "{project["name"]}=={project["version"]}"'
    ).encode()

    assert package_readme == readme
    assert b"python -m pip install ." in readme
    assert f"{project['name']}-{project['version']}-py3-none-any.whl".encode() in readme
    assert index_install in readme
    assert b"Package-index availability is established by" in readme
    assert f"If version `{project['version']}` is present on PyPI".encode() in readme
    assert b"Otherwise, use the source or admitted local-wheel commands" in readme
    assert b"research/reference artifact, not a production" in readme
    contributing = (repository_root / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "`README.md` owns" in contributing
    assert "`PACKAGE_README.md` is its byte-identical packaging projection" in (
        contributing
    )


def test_release_runbook_keeps_direct_index_claims_downstream_of_readback(
    repository_root: Path,
) -> None:
    runbook = (repository_root / "RELEASING.md").read_text(encoding="utf-8")
    normalized = " ".join(runbook.split())

    assert "environments named exactly `testpypi` and `pypi`" in runbook
    assert "deployments from the `main` branch only" in runbook
    assert "Require an operator review on `pypi`" in runbook
    assert "owner `belgi-protocol`, repository `belgi-reference`" in runbook
    assert "`confirmation`: `publish belgi==0.1.0a0 from v0.1.0a0`" in runbook
    assert "do not start a new dispatch or use **Re-run all jobs**" in normalized
    assert "use **Re-run failed jobs** on the same workflow run" in normalized
    assert "prepare a new Python version and annotated tag" in normalized
    assert "active repository tag ruleset for `v*`" in normalized
    assert "update and deletion restricted and no bypass actor" in normalized
    assert "immediately before every index upload" in normalized
    assert "describes the exact-version index command conditionally" in normalized
    assert "Only after the PyPI readback job succeeds" in normalized
    assert "direct package-index availability statement" in normalized
