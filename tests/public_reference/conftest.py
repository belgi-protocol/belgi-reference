from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    repository_root = config.rootpath.resolve(strict=True)
    if not (repository_root / "belgi" / "product").is_dir():
        return
    public_test_root = Path(__file__).resolve().parent
    marker = pytest.mark.skip(
        reason="public-reference behavior runs only in the exported repository"
    )
    for item in items:
        if Path(item.path).resolve().is_relative_to(public_test_root):
            item.add_marker(marker)


@pytest.fixture(scope="session")
def repository_root(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath.resolve(strict=True)


def run_belgi(
    *arguments: str,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "belgi", *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def stdout_json(process: subprocess.CompletedProcess[str]) -> dict[str, object]:
    document = json.loads(process.stdout)
    assert isinstance(document, dict)
    return document
