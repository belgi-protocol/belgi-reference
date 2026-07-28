"""Resolved reference-profile judged endpoint values."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ReferenceProfileJudgedCarrierEndpoint"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileJudgedCarrierEndpoint:
    content: object
