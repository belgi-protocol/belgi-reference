"""Core Sat registrations for exact Part 4 finite semantics."""

from __future__ import annotations

from typing import Any, cast

from belgi.core import SatRegistration
from belgi.profile.edition import ExactEditionBinding
from belgi.profile.reference_profile.evaluator.semantics.contracts import (
    SemanticsProviderWitness,
)

from .constants import (
    CHANGE_BASIS_SEMANTICS,
    PART4_DESIGNATOR,
    REQUIRED_EVIDENCE_SEMANTICS,
    REVIEW_POLICY_SEMANTICS,
)
from .semantics import (
    change_basis_resolved_sat,
    finite_required_evidence_present_sat,
    review_policy_satisfied_sat,
)


def finite_evaluator_sat_registrations(
    *, profile_binding: ExactEditionBinding
) -> tuple[SatRegistration, ...]:
    """Bind finite Sat callables only to the exact Part 4 source."""

    profile_designator = profile_binding.immutable_designator
    if (
        profile_designator.uri != PART4_DESIGNATOR.uri
        or profile_designator.digest.algorithm_id
        != PART4_DESIGNATOR.digest.algorithm_id
        or profile_designator.digest.digest_value
        != PART4_DESIGNATOR.digest.digest_value
    ):
        raise ValueError("finite evaluator registrations require exact Part 4.")
    registrations = (
        (CHANGE_BASIS_SEMANTICS, change_basis_resolved_sat),
        (REQUIRED_EVIDENCE_SEMANTICS, finite_required_evidence_present_sat),
        (REVIEW_POLICY_SEMANTICS, review_policy_satisfied_sat),
    )
    for _, implementation in registrations:
        cast(
            Any, implementation
        ).__belgi_provider_entrypoint__ = (
            f"{implementation.__module__}:{implementation.__qualname__}"
        )
    return tuple(
        SatRegistration(
            semantics_key=semantics_key,
            sat=implementation,
            provider_witnesses=(
                SemanticsProviderWitness(
                    semantics_key=semantics_key,
                    source_designator=profile_designator,
                    provider_identifier="belgi.software-change.finite-review-record",
                    callable_entrypoint=(
                        f"{implementation.__module__}:{implementation.__qualname__}"
                    ),
                ),
            ),
        )
        for semantics_key, implementation in registrations
    )
