"""Bounded CI companion vocabulary implemented by the reference runtime."""

from __future__ import annotations

from .identifiers.environment import (
    RUN_IDENTITY,
    SOURCE_REFERENCE_IDENTITY,
    WORKFLOW_DEFINITION_IDENTITY,
)
from .identifiers.sources import RUN_RECORD

__all__ = [
    "SUPPORTED_CI_ENVIRONMENT_TERMS",
    "SUPPORTED_CI_SOURCE_MATERIAL_ROLES",
]


SUPPORTED_CI_SOURCE_MATERIAL_ROLES = (RUN_RECORD,)
SUPPORTED_CI_ENVIRONMENT_TERMS = (
    RUN_IDENTITY,
    WORKFLOW_DEFINITION_IDENTITY,
    SOURCE_REFERENCE_IDENTITY,
)
