from __future__ import annotations

import json
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest

from tests.public_reference.distribution_contract import (
    ALLOWED_REFERENCE_CARRIER_PACKAGE_MODULES,
    PRIVATE_KEY_IMPLEMENTATION_MARKERS,
    UNSHIPPED_CRYPTO_CAPABILITIES,
    UNSHIPPED_REFERENCE_MODULE_DESTINATIONS,
)

_FORBIDDEN_WHEEL_FRAGMENTS = (
    "belgi/product/",
    "/operational_action/",
    "belgi/carrier/integrity/signing/",
    "belgi/carrier/package/assembly/",
    "belgi/carrier/package/emission/",
    "belgi/profile/dispatch/",
    "belgi/replay/conformance/api.py",
    "belgi/replay/procedure/conformance/",
    "belgi/replay/reference_profile/conformance/",
    "belgi/replay/reference_profile/finite_evaluator/conformance/signed_witness/",
    "belgi/replay/report_conformance/",
    "belgi/substrate/subprocess/",
    "belgi/substrate/yaml/",
)
_REQUIRED_SOURCE_STATE_WHEEL_ENTRIES = frozenset(
    {
        "belgi/profile/reference_profile/judged/source_state.py",
        "belgi/replay/reference_profile/judged/part4_source_state.py",
    }
)


def test_project_metadata_declares_only_the_reference_distribution(
    repository_root: Path,
) -> None:
    project = tomllib.loads(
        (repository_root / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert project["project"]["name"] == "belgi"
    assert project["project"]["scripts"] == {"belgi": "belgi.cli:main"}
    assert "optional-dependencies" not in project["project"]
    assert all(
        "invalid" not in url and "belgi.dev" not in url
        for url in project["project"]["urls"].values()
    )
    package_data = project["tool"]["setuptools"]["package-data"]["belgi"]
    assert not any("product/" in item for item in package_data)
    assert not any("reference_profile/conformance/" in item for item in package_data)
    assert "exclude" not in project["tool"]["setuptools"]["packages"]["find"]


def test_only_promised_import_is_passive_and_product_free(
    repository_root: Path,
) -> None:
    script = """
import json
import sys
import belgi
assert belgi.__all__ == ["__version__"]
forbidden = [
    name for name in sys.modules
    if name.startswith((
        "belgi.product",
        "belgi.carrier.operational_action",
        "belgi.profile.operational_action",
        "belgi.replay.operational_action",
    ))
]
print(json.dumps({"version": belgi.__version__, "forbidden": forbidden}))
"""
    process = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    assert '"forbidden": []' in process.stdout


def test_profile_initializer_is_passive(repository_root: Path) -> None:
    script = """
import json
import sys
import belgi.profile
loaded_children = sorted(
    name for name in sys.modules if name.startswith("belgi.profile.")
)
print(json.dumps({
    "exports": belgi.profile.__all__,
    "loadedChildren": loaded_children,
}))
"""
    process = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout) == {
        "exports": [],
        "loadedChildren": [],
    }


def test_verifier_source_excludes_producer_and_dormant_capabilities(
    repository_root: Path,
) -> None:
    script = """
import importlib
import json
from pathlib import Path
import belgi.substrate.crypto as verifier_crypto

root = Path.cwd()
unexpected_files = sorted(
    item
    for item in UNSHIPPED
    if (root / item).is_file()
)
unexpected_imports = []
for item in UNSHIPPED:
    module_name = item.removesuffix("/__init__.py").removesuffix(".py").replace("/", ".")
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name is None or not (
            exc.name == module_name or module_name.startswith(exc.name + ".")
        ):
            raise
    else:
        unexpected_imports.append(module_name)
unexpected_crypto = sorted(
    name for name in CRYPTO_CAPABILITIES if hasattr(verifier_crypto, name)
)
print(json.dumps({
    "unexpectedFiles": unexpected_files,
    "unexpectedImports": unexpected_imports,
    "unexpectedCrypto": unexpected_crypto,
}))
"""
    source = (
        "UNSHIPPED = "
        f"{sorted(UNSHIPPED_REFERENCE_MODULE_DESTINATIONS)!r}\n"
        "CRYPTO_CAPABILITIES = "
        f"{sorted(UNSHIPPED_CRYPTO_CAPABILITIES)!r}\n" + script
    )
    process = subprocess.run(
        [sys.executable, "-c", source],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout) == {
        "unexpectedFiles": [],
        "unexpectedImports": [],
        "unexpectedCrypto": [],
    }
    carrier_package_modules = {
        path.relative_to(repository_root).as_posix()
        for path in (repository_root / "belgi/carrier/package").rglob("*.py")
    }
    assert carrier_package_modules == ALLOWED_REFERENCE_CARRIER_PACKAGE_MODULES

    python_sources = b"\n".join(
        path.read_bytes() for path in (repository_root / "belgi").rglob("*.py")
    )
    assert not any(
        marker in python_sources for marker in PRIVATE_KEY_IMPLEMENTATION_MARKERS
    )


def test_built_wheel_inventory_when_supplied() -> None:
    import os

    wheel_text = os.environ.get("BELGI_WHEEL_PATH")
    if wheel_text is None:
        pytest.skip("set BELGI_WHEEL_PATH to audit an exact built wheel")
    wheel = Path(wheel_text)

    with zipfile.ZipFile(wheel) as archive:
        names = tuple(archive.namelist())
        python_sources = b"\n".join(
            archive.read(name) for name in names if name.endswith(".py")
        )

    assert any(name.endswith(".dist-info/entry_points.txt") for name in names)
    assert any(
        name.endswith("share/belgi/examples/finite-review-record/claim-record.json")
        for name in names
    )
    assert any(
        name.endswith(
            "share/belgi/examples/finite-review-record-tampered/claim-record.json"
        )
        for name in names
    )
    assert _REQUIRED_SOURCE_STATE_WHEEL_ENTRIES <= set(names)
    assert UNSHIPPED_REFERENCE_MODULE_DESTINATIONS.isdisjoint(names)
    assert {
        name
        for name in names
        if name.startswith("belgi/carrier/package/") and name.endswith(".py")
    } == ALLOWED_REFERENCE_CARRIER_PACKAGE_MODULES
    assert not any(
        marker in python_sources for marker in PRIVATE_KEY_IMPLEMENTATION_MARKERS
    )
    assert not any(
        fragment in name for name in names for fragment in _FORBIDDEN_WHEEL_FRAGMENTS
    )
    git_sources = {
        name
        for name in names
        if name.startswith("belgi/substrate/git/") and name.endswith(".py")
    }
    assert git_sources == {
        "belgi/substrate/git/__init__.py",
        "belgi/substrate/git/identity.py",
    }
    for product_import_marker in (
        b"from belgi.product",
        b"import belgi.product",
    ):
        assert product_import_marker not in python_sources
