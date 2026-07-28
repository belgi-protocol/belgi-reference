from __future__ import annotations

import sys as _sys
from importlib import import_module as _import_module
from typing import Any


def import_module_by_name(module_name: str) -> Any:
    return _import_module(module_name)


def is_loaded_type_identity(value_type: type[object]) -> bool:
    """Return whether a type is the exact object installed at its declared path."""

    module_name = value_type.__module__
    qualname = value_type.__qualname__
    if "<locals>" in qualname:
        return False
    try:
        owner: object = _sys.modules[module_name]
        for component in qualname.split("."):
            owner = getattr(owner, component)
    except (AttributeError, KeyError):
        return False
    return owner is value_type


__all__ = ["import_module_by_name", "is_loaded_type_identity"]
