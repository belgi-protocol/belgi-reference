from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path
from types import ModuleType


def _environment_python(environment: Path) -> Path:
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    return scripts / ("python.exe" if os.name == "nt" else "python")


def test_installed_identity_cannot_be_shadowed_by_source_checkout(
    tmp_path: Path,
    installed_module: ModuleType,
) -> None:
    environment = tmp_path / "installed"
    venv.EnvBuilder(with_pip=False).create(environment)
    python = _environment_python(environment)
    purelib = Path(
        subprocess.run(
            [
                str(python),
                "-c",
                "import sysconfig; print(sysconfig.get_path('purelib'))",
            ],
            check=True,
            capture_output=True,
            cwd=environment,
            text=True,
        ).stdout.strip()
    )
    package = purelib / "belgi"
    package.mkdir()
    (package / "__init__.py").write_text(
        "__all__ = ['__version__']\n__version__ = 'installed-shadow-witness'\n",
        encoding="utf-8",
    )

    observed_prefix = installed_module._installed_prefix(
        environment=environment,
        python=python,
        expected_version="installed-shadow-witness",
    )

    assert observed_prefix == environment.resolve(strict=True)


def test_installed_typing_cannot_be_shadowed_by_source_checkout(
    tmp_path: Path,
) -> None:
    environment = tmp_path / "installed"
    venv.EnvBuilder(with_pip=False).create(environment)
    python = _environment_python(environment)
    purelib = Path(
        subprocess.run(
            [
                str(python),
                "-c",
                "import sysconfig; print(sysconfig.get_path('purelib'))",
            ],
            check=True,
            capture_output=True,
            cwd=environment,
            text=True,
        ).stdout.strip()
    )
    package = purelib / "belgi"
    package.mkdir()
    (package / "__init__.py").write_text(
        "__version__: int = 1\n",
        encoding="utf-8",
    )
    (package / "py.typed").write_bytes(b"")
    consumer = tmp_path / "typing-consumer"
    consumer.mkdir()
    (consumer / "typing_consumer.py").write_text(
        "from belgi import __version__\ninstalled_version: int = __version__\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pyright",
            "--pythonpath",
            str(python),
            "typing_consumer.py",
        ],
        check=False,
        capture_output=True,
        cwd=consumer,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
