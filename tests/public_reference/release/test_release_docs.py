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
    index_page = (
        f"https://pypi.org/project/{project['name']}/{project['version']}/"
    ).encode()

    assert package_readme == readme
    assert project["readme"] == "PACKAGE_README.md"
    assert b"python -m pip install ." in readme
    assert f"{project['name']}-{project['version']}-py3-none-any.whl".encode() in readme
    assert index_install in readme
    assert index_page in readme
    assert b"Install the exact alpha release from" in readme
    assert b"If version" not in readme
    assert b"Otherwise, use the source or admitted local-wheel commands" not in readme
    assert b"research/reference artifact, not a production" in readme
    contributing = (repository_root / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "`README.md` owns" in contributing
    assert "`PACKAGE_README.md` is its byte-identical packaging projection" in (
        contributing
    )


def test_release_runbook_records_direct_index_claim_after_readback(
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
    assert "PyPI readback for `0.1.0a0` succeeded" in normalized
    assert "`README.md` and `PACKAGE_README.md` remain byte-identical" in normalized
    assert "does not rewrite already-published `0.1.0a0` metadata" in normalized
    assert "never reuse an index version or move its tag to update prose" in normalized
