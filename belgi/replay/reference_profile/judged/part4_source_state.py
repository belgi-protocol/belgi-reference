from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier import CanonicalReference, ClaimRecord, MemberName
from belgi.profile.reference_profile.judged import (
    ReferenceProfileSourceStateError,
    has_reference_profile_judged_source_state_vocabulary,
    require_reference_profile_judged_source_state,
)
from belgi.replay.lifting.exceptions import ResolveFailureError
from belgi.replay.lifting.model import ResolvedPackageMember
from belgi.substrate.hash import sha256_bytes

__all__ = ["Part4JudgedSourceStateExtension"]

_PATCH_MEMBER_NAME = MemberName("proposed-change-patch")
_CONTEXT_MEMBER_PREFIX = "proposed-change-context-"


class Part4JudgedSourceStateExtension:
    """Bind Part 4 source-state meaning to authenticated package members."""

    def applies(
        self,
        *,
        proposal: Mapping[str, object],
        claim_record: ClaimRecord,
    ) -> bool:
        return bool(_source_state_input_names(claim_record=claim_record)) or (
            has_reference_profile_judged_source_state_vocabulary(proposal=proposal)
        )

    def require_recovery(
        self,
        *,
        proposal: Mapping[str, object],
        baseline: Mapping[str, object],
        recovered: tuple[ResolvedPackageMember, ...],
        claim_record: ClaimRecord,
        root_reference: CanonicalReference,
    ) -> None:
        try:
            source_state = require_reference_profile_judged_source_state(
                proposal=proposal,
                baseline=baseline,
            )
        except ReferenceProfileSourceStateError as exc:
            raise ResolveFailureError(
                message=exc.detail,
                related_reference=root_reference,
            ) from exc
        expected = (
            *(
                ((_PATCH_MEMBER_NAME, source_state.patch_digest),)
                if source_state.patch_digest is not None
                else ()
            ),
            *(
                (
                    MemberName(f"{_CONTEXT_MEMBER_PREFIX}{ordinal:03d}"),
                    digest,
                )
                for ordinal, digest in enumerate(
                    source_state.context_digests,
                    start=1,
                )
            ),
        )
        _require_source_state_input_bytes(
            recovered=recovered,
            authenticated_names=_source_state_input_names(claim_record=claim_record),
            expected=expected,
            root_reference=root_reference,
        )


def _source_state_input_names(
    *,
    claim_record: ClaimRecord,
) -> tuple[MemberName, ...]:
    return tuple(
        entry.member_name
        for entry in claim_record.member_inventory.entries
        if _is_source_state_input_name(member_name=entry.member_name)
    )


def _is_source_state_input_name(*, member_name: MemberName) -> bool:
    return member_name == _PATCH_MEMBER_NAME or str(member_name).startswith(
        _CONTEXT_MEMBER_PREFIX
    )


def _require_source_state_input_bytes(
    *,
    recovered: tuple[ResolvedPackageMember, ...],
    authenticated_names: tuple[MemberName, ...],
    expected: tuple[tuple[MemberName, str], ...],
    root_reference: CanonicalReference,
) -> None:
    recovered_by_name = {
        dependency.inventory_entry.member_name: dependency for dependency in recovered
    }
    expected_names = {name for name, _digest in expected}
    if (
        set(authenticated_names) != expected_names
        or set(recovered_by_name) != expected_names
    ):
        raise ResolveFailureError(
            message=(
                "Part 4 judged inputs are missing, extra, wrongly associated, "
                "or out of order."
            ),
            related_reference=root_reference,
        )
    for member_name, expected_digest in expected:
        dependency = recovered_by_name[member_name]
        if sha256_bytes(dependency.preserved_bytes) != expected_digest:
            raise ResolveFailureError(
                message=(
                    f"Part 4 judged input {member_name!s} does not bind its "
                    "claimed digest."
                ),
                related_reference=dependency.canonical_reference,
            )
