from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from belgi.profile.governance import FailureId

__all__ = [
    "CountTolerance",
    "RatioTolerance",
    "SeverityLevel",
    "SeverityTolerance",
]


class SeverityLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True, kw_only=True)
class CountTolerance:
    identifier: FailureId
    maximum_count: int

    def __post_init__(self) -> None:
        if self.maximum_count < 0:
            raise ValueError("maximum_count must be non-negative.")


@dataclass(frozen=True, slots=True, kw_only=True)
class RatioTolerance:
    identifier: FailureId
    minimum_ratio: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_ratio <= 1.0:
            raise ValueError("minimum_ratio must be in the closed interval [0.0, 1.0].")


@dataclass(frozen=True, slots=True, kw_only=True)
class SeverityTolerance:
    identifier: FailureId
    maximum_severity: SeverityLevel
