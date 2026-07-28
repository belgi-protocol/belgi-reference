"""Replay lifting exception hierarchy and stage identifiers."""

from __future__ import annotations

from typing import NewType

from belgi.carrier import CanonicalReference

__all__ = [
    "INDUCE_STAGE",
    "PARSE_STAGE",
    "RESOLVE_STAGE",
    "AmbientContextRequiredError",
    "InduceFailureError",
    "IntegrityVerificationError",
    "LiftingStage",
    "LiftingStageError",
    "PackageReadError",
    "ParseFailureError",
    "ReplayError",
    "ResolveFailureError",
]


LiftingStage = NewType("LiftingStage", str)

PARSE_STAGE = LiftingStage("parse")
RESOLVE_STAGE = LiftingStage("resolve")
INDUCE_STAGE = LiftingStage("induce")


class ReplayError(Exception):
    """Base exception for replay-time failures internal to the replay layer."""


class PackageReadError(ReplayError):
    """A required replay-package member could not be read as preserved."""


class IntegrityVerificationError(ReplayError):
    """Replay-time integrity verification failed or could not be completed."""


class LiftingStageError(ReplayError):
    def __init__(
        self,
        *,
        stage: LiftingStage,
        message: str,
        related_reference: CanonicalReference | None = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.related_reference = related_reference


class ParseFailureError(LiftingStageError):
    def __init__(
        self,
        *,
        message: str,
        related_reference: CanonicalReference | None = None,
    ) -> None:
        super().__init__(
            stage=PARSE_STAGE,
            message=message,
            related_reference=related_reference,
        )


class ResolveFailureError(LiftingStageError):
    def __init__(
        self,
        *,
        message: str,
        related_reference: CanonicalReference | None = None,
    ) -> None:
        super().__init__(
            stage=RESOLVE_STAGE,
            message=message,
            related_reference=related_reference,
        )


class AmbientContextRequiredError(ResolveFailureError):
    """Raised when replay resolution requires undeclared ambient context."""


class InduceFailureError(LiftingStageError):
    def __init__(
        self,
        *,
        message: str,
        related_reference: CanonicalReference | None = None,
    ) -> None:
        super().__init__(
            stage=INDUCE_STAGE,
            message=message,
            related_reference=related_reference,
        )
