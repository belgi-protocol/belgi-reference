from __future__ import annotations

from dataclasses import dataclass

__all__ = ["AdmissionSubject"]


@dataclass(frozen=True, slots=True, kw_only=True)
class AdmissionSubject:
    value: object
