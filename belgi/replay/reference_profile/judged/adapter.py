from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    DependencyKind,
    JudgedObjectCarrier,
    MemberInventoryEntry,
    ReferencedSourceKind,
)
from belgi.core import JudgedObject
from belgi.profile.reference_profile.judged import (
    reference_profile_judged_object_from_carrier_endpoints,
)
from belgi.replay.carriers.content import resolved_content_locator_json_object
from belgi.replay.lifting.exceptions import ResolveFailureError
from belgi.replay.lifting.model import (
    LiftedCarrier,
    ParsedCarrier,
    ResolvedCarrier,
    ResolvedDependencies,
    ResolvedPackageMember,
)
from belgi.replay.parsing import (
    dependency_references_for_member_names,
    require_inline_json_object,
)
from belgi.replay.reference_profile.source_authority import (
    Part4RootAuthority,
    exact_part4_carrier_designator,
    part4_root_authority,
    require_resolved_source_authority,
    root_references_part4_source,
)

from .generic_source_state import (
    generic_source_state_dependency_references,
    recover_generic_source_state_inputs,
    require_generic_source_state_records,
    require_generic_source_state_recovery,
)
from .model import ReferenceProfileJudgedCarrierEndpoint
from .parsing import parse_judged_object_carrier
from .source_state import (
    finite_source_state_dependency_references,
    require_finite_source_state_recovery,
)

__all__ = [
    "JudgedObjectReferenceProfileAdapter",
    "JudgedSourceStateExtension",
]


class JudgedSourceStateExtension(Protocol):
    def applies(
        self,
        *,
        proposal: Mapping[str, object],
        claim_record: ClaimRecord,
    ) -> bool: ...

    def require_recovery(
        self,
        *,
        proposal: Mapping[str, object],
        baseline: Mapping[str, object],
        recovered: tuple[ResolvedPackageMember, ...],
        claim_record: ClaimRecord,
        root_reference: CanonicalReference,
    ) -> None: ...


class JudgedObjectReferenceProfileAdapter:
    def __init__(
        self,
        *,
        source_state_extension: JudgedSourceStateExtension | None = None,
    ) -> None:
        self._source_state_extension = source_state_extension

    def parse(
        self,
        *,
        root_member: MemberInventoryEntry,
        root_bytes: bytes,
        claim_record: ClaimRecord,
    ) -> ParsedCarrier[JudgedObjectCarrier]:
        carrier = parse_judged_object_carrier(
            root_bytes=root_bytes,
            description="judged-object carrier",
            claim_record=claim_record,
        )
        carrier_dependencies = dependency_references_for_member_names(
            member_names=carrier.referenced_member_names(),
            claim_record=claim_record,
        )
        source_state_dependencies = _source_state_dependencies_for_parse(
            carrier=carrier,
            claim_record=claim_record,
            root_member=root_member,
        )
        return ParsedCarrier(
            root_member=root_member,
            root_bytes=root_bytes,
            parsed_carrier=carrier,
            dependency_references=tuple(
                dict.fromkeys(carrier_dependencies + source_state_dependencies)
            ),
            exact_edition_designators=(
                (exact_part4_carrier_designator(),)
                if root_references_part4_source(
                    claim_record=claim_record,
                    root_member=root_member,
                )
                else ()
            ),
        )

    def resolve(
        self,
        *,
        parsed: ParsedCarrier[JudgedObjectCarrier],
        dependencies: ResolvedDependencies,
        claim_record: ClaimRecord,
    ) -> ResolvedCarrier[JudgedObjectCarrier]:
        authority = part4_root_authority(
            claim_record=claim_record,
            root_member=parsed.root_member,
        )
        if authority is Part4RootAuthority.ABSENT:
            proposal, baseline = self._resolved_source_state_records(
                parsed=parsed,
                dependencies=dependencies,
                claim_record=claim_record,
            )
            extension = self._source_state_extension
            if extension is not None and extension.applies(
                proposal=proposal,
                claim_record=claim_record,
            ):
                raise ResolveFailureError(
                    message=(
                        "The selected judged source-state extension requires an exact "
                        "Part 4 profile-material ownership edge."
                    ),
                    related_reference=parsed.root_member.canonical_reference,
                )
            require_generic_source_state_records(
                proposal=proposal,
                baseline=baseline,
                root_reference=parsed.root_member.canonical_reference,
            )
        if authority is not Part4RootAuthority.ABSENT:
            require_resolved_source_authority(
                resolved=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
                designator=exact_part4_carrier_designator(),
                allowed_roles=_part4_source_roles(authority=authority),
            )
        if authority is Part4RootAuthority.DETERMINING_SEMANTICS:
            require_finite_source_state_recovery(
                carrier=parsed.parsed_carrier,
                dependencies=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
            )
        elif authority is Part4RootAuthority.OWNERSHIP:
            self._require_ownership_source_state_recovery(
                parsed=parsed,
                dependencies=dependencies,
                claim_record=claim_record,
            )
        return ResolvedCarrier(
            root_member=parsed.root_member,
            resolved_carrier=parsed.parsed_carrier,
            dependencies=dependencies,
        )

    def _require_ownership_source_state_recovery(
        self,
        *,
        parsed: ParsedCarrier[JudgedObjectCarrier],
        dependencies: ResolvedDependencies,
        claim_record: ClaimRecord,
    ) -> None:
        extension = self._source_state_extension
        proposal, baseline = self._resolved_source_state_records(
            parsed=parsed,
            dependencies=dependencies,
            claim_record=claim_record,
        )
        if extension is None or not extension.applies(
            proposal=proposal,
            claim_record=claim_record,
        ):
            require_generic_source_state_recovery(
                carrier=parsed.parsed_carrier,
                dependencies=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
            )
            return
        root_reference = parsed.root_member.canonical_reference
        if root_reference is None:
            raise ResolveFailureError(
                message="Judged-object root lacks a canonical reference."
            )
        extension.require_recovery(
            proposal=proposal,
            baseline=baseline,
            recovered=recover_generic_source_state_inputs(
                dependencies=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
            ),
            claim_record=claim_record,
            root_reference=root_reference,
        )

    @staticmethod
    def _resolved_source_state_records(
        *,
        parsed: ParsedCarrier[JudgedObjectCarrier],
        dependencies: ResolvedDependencies,
        claim_record: ClaimRecord,
    ) -> tuple[Mapping[str, object], Mapping[str, object]]:
        return (
            resolved_content_locator_json_object(
                locator=parsed.parsed_carrier.proposal,
                dependencies=dependencies,
                claim_record=claim_record,
                description="judged-object carrier.proposal",
            ),
            resolved_content_locator_json_object(
                locator=parsed.parsed_carrier.baseline,
                dependencies=dependencies,
                claim_record=claim_record,
                description="judged-object carrier.baseline",
            ),
        )

    def induce(
        self,
        *,
        resolved: ResolvedCarrier[JudgedObjectCarrier],
        claim_record: ClaimRecord,
    ) -> LiftedCarrier[JudgedObject]:
        authority = part4_root_authority(
            claim_record=claim_record,
            root_member=resolved.root_member,
        )
        return LiftedCarrier(
            root_member=resolved.root_member,
            semantic_object=reference_profile_judged_object_from_carrier_endpoints(
                proposal=ReferenceProfileJudgedCarrierEndpoint(
                    content=require_inline_json_object(
                        locator=resolved.resolved_carrier.proposal,
                        description="judged-object carrier.proposal",
                    ),
                ),
                baseline=ReferenceProfileJudgedCarrierEndpoint(
                    content=require_inline_json_object(
                        locator=resolved.resolved_carrier.baseline,
                        description="judged-object carrier.baseline",
                    ),
                ),
                resolved_determining_source_designators=(
                    (exact_part4_carrier_designator(),)
                    if authority is Part4RootAuthority.DETERMINING_SEMANTICS
                    else ()
                ),
            ),
        )


def _part4_source_roles(
    *, authority: Part4RootAuthority
) -> tuple[tuple[ReferencedSourceKind, DependencyKind], ...]:
    if authority is Part4RootAuthority.DETERMINING_SEMANTICS:
        return (
            (
                ReferencedSourceKind.DETERMINING_SEMANTICS,
                DependencyKind.DETERMINING_SEMANTICS,
            ),
        )
    return ((ReferencedSourceKind.PROFILE, DependencyKind.PROFILE_MATERIAL),)


def _source_state_dependencies_for_parse(
    *,
    carrier: JudgedObjectCarrier,
    claim_record: ClaimRecord,
    root_member: MemberInventoryEntry,
) -> tuple[CanonicalReference, ...]:
    """Discover source-state inputs without moving authority failures into parsing."""

    try:
        authority = part4_root_authority(
            claim_record=claim_record,
            root_member=root_member,
        )
    except ResolveFailureError:
        return ()
    if authority is Part4RootAuthority.DETERMINING_SEMANTICS:
        return finite_source_state_dependency_references(carrier=carrier)
    if authority is Part4RootAuthority.OWNERSHIP:
        return generic_source_state_dependency_references(
            claim_record=claim_record,
            root_member=root_member,
        )
    return ()
