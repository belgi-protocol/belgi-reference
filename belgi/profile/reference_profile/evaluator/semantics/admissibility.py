from __future__ import annotations

from belgi.core import SatRegistry
from belgi.profile.edition import ExactEditionBinding

from .registry import register_reference_profile_semantics

__all__ = ["build_reference_profile_evaluator_sat_registry"]


def build_reference_profile_evaluator_sat_registry(
    *, edition_bindings: tuple[ExactEditionBinding, ...] | None = None
) -> SatRegistry:
    return register_reference_profile_semantics(
        registry=SatRegistry.empty(),
        edition_bindings=edition_bindings,
    )
