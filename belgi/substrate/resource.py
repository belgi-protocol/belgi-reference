from __future__ import annotations

from importlib import resources as _resources
from pathlib import Path


def load_packaged_bytes(
    *,
    package_name: str,
    path_parts: tuple[str, ...],
    label: str,
) -> bytes:
    try:
        node = _resources.files(package_name)
        for part in path_parts:
            node = node.joinpath(part)
        return node.read_bytes()
    except Exception as exc:
        raise ValueError(f"Could not load packaged bytes {label}.") from exc


def copy_packaged_directory(
    *,
    package_name: str,
    path_parts: tuple[str, ...],
    destination: Path,
    label: str,
) -> Path:
    if destination.exists():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    try:
        node = _resources.files(package_name)
        for part in path_parts:
            node = node.joinpath(part)
        for member in node.iterdir():
            if member.is_file():
                (destination / member.name).write_bytes(member.read_bytes())
    except Exception as exc:
        raise ValueError(f"Could not copy packaged directory {label}.") from exc
    return destination


__all__ = [
    "copy_packaged_directory",
    "load_packaged_bytes",
]
