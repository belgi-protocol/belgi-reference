from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    ClaimRecord,
    DependencyKind,
    EvaluatorCarrier,
    MemberInventoryEntry,
    ReferencedSourceKind,
)
from belgi.core import (
    Evaluator,
)
from belgi.replay.carriers import parse_evaluator_carrier
from belgi.replay.lifting.model import (
    LiftedCarrier,
    ParsedCarrier,
    ResolvedCarrier,
    ResolvedDependencies,
)
from belgi.replay.reference_profile.source_authority import (
    Part4RootAuthority,
    exact_part4_carrier_designator,
    part4_root_authority,
    require_resolved_source_authority,
    root_references_part4_source,
)

from .lifting import reference_profile_evaluator_from_carrier

__all__ = ["EvaluatorReferenceProfileAdapter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluatorReferenceProfileAdapter:
    provider_witnesses: tuple[object, ...] = ()

    def parse(
        self,
        *,
        root_member: MemberInventoryEntry,
        root_bytes: bytes,
        claim_record: ClaimRecord,
    ) -> ParsedCarrier[EvaluatorCarrier]:
        carrier = parse_evaluator_carrier(
            root_bytes=root_bytes,
            description="evaluator carrier",
        )
        exact_designators = list(carrier.required_referenced_source_designators())
        if root_references_part4_source(
            claim_record=claim_record,
            root_member=root_member,
        ):
            exact_designators.append(exact_part4_carrier_designator())
        return ParsedCarrier(
            root_member=root_member,
            root_bytes=root_bytes,
            parsed_carrier=carrier,
            dependency_references=(),
            exact_edition_designators=tuple(dict.fromkeys(exact_designators)),
        )

    def resolve(
        self,
        *,
        parsed: ParsedCarrier[EvaluatorCarrier],
        dependencies: ResolvedDependencies,
        claim_record: ClaimRecord,
    ) -> ResolvedCarrier[EvaluatorCarrier]:
        authority = part4_root_authority(
            claim_record=claim_record,
            root_member=parsed.root_member,
        )
        if authority is not Part4RootAuthority.ABSENT:
            require_resolved_source_authority(
                resolved=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
                designator=exact_part4_carrier_designator(),
                allowed_roles=(
                    (
                        ReferencedSourceKind.DETERMINING_SEMANTICS,
                        DependencyKind.DETERMINING_SEMANTICS,
                    ),
                )
                if authority is Part4RootAuthority.DETERMINING_SEMANTICS
                else ((ReferencedSourceKind.PROFILE, DependencyKind.PROFILE_MATERIAL),),
            )
        return ResolvedCarrier(
            root_member=parsed.root_member,
            resolved_carrier=parsed.parsed_carrier,
            dependencies=dependencies,
        )

    def induce(
        self,
        *,
        resolved: ResolvedCarrier[EvaluatorCarrier],
        claim_record: ClaimRecord,
    ) -> LiftedCarrier[Evaluator]:
        return LiftedCarrier(
            root_member=resolved.root_member,
            semantic_object=reference_profile_evaluator_from_carrier(
                evaluator_carrier=resolved.resolved_carrier,
                referenced_sources=resolved.dependencies.referenced_sources,
                provider_witnesses=self.provider_witnesses,
                finite_selection_authorized=(
                    part4_root_authority(
                        claim_record=claim_record,
                        root_member=resolved.root_member,
                    )
                    is Part4RootAuthority.DETERMINING_SEMANTICS
                ),
            ),
        )
