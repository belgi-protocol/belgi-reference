"""Bounded Python companion surface implemented by the reference runtime."""

from __future__ import annotations

from belgi.profile.governance import ConditionId

from .identifiers.conditions import TESTS_PASS

__all__ = ["SUPPORTED_PYTHON_CONDITIONS"]


SUPPORTED_PYTHON_CONDITIONS: tuple[ConditionId, ...] = (TESTS_PASS,)
