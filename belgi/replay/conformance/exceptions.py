"""Installed replay-conformance exceptions."""

from __future__ import annotations


class InstalledConformanceError(RuntimeError):
    """Raised when installed exact resources cannot be executed."""


__all__ = ["InstalledConformanceError"]
