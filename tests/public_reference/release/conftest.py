from __future__ import annotations

import importlib
import importlib.util
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture(scope="session")
def release_modules(
    repository_root: Path,
) -> Iterator[tuple[ModuleType, ModuleType, ModuleType]]:
    scripts = repository_root / ".github" / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        candidate = importlib.import_module("release_support.candidate")
        common = importlib.import_module("release_support.common")
        index = importlib.import_module("release_support.index")
        yield candidate, common, index
    finally:
        sys.path.remove(str(scripts))


@pytest.fixture(scope="session")
def installed_module(repository_root: Path) -> Iterator[ModuleType]:
    scripts = repository_root / ".github" / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        yield importlib.import_module("release_support.installed")
    finally:
        sys.path.remove(str(scripts))


@pytest.fixture(scope="session")
def archives_module(repository_root: Path) -> Iterator[ModuleType]:
    scripts = repository_root / ".github" / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        yield importlib.import_module("release_support.archives")
    finally:
        sys.path.remove(str(scripts))


@pytest.fixture(scope="session")
def release_tag_module(repository_root: Path) -> ModuleType:
    path = repository_root / ".github" / "scripts" / "release_tag.py"
    specification = importlib.util.spec_from_file_location(
        "belgi_release_tag",
        path,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module
