"""Claim-record validation helpers."""

from __future__ import annotations

from typing import Protocol

from belgi.carrier.exceptions import (
    ClaimRecordError,
    DependencyDeclarationError,
    ReferencedSourceError,
    RootDesignationError,
)
from belgi.carrier.integrity import (
    PACKAGE_INTEGRITY_ANCHOR_MEDIA_TYPE,
    PACKAGE_INTEGRITY_ANCHOR_SCHEMA_DESIGNATOR,
    PACKAGE_INTEGRITY_MANIFEST_MEDIA_TYPE,
    PACKAGE_INTEGRITY_MANIFEST_SCHEMA_DESIGNATOR,
)
from belgi.carrier.inventory import (
    CanonicalReference,
    ImmutableDesignator,
    MemberClassification,
    MemberInventory,
    MemberName,
    MemberRole,
    PackageIdentifier,
)

__all__ = ["validate_claim_record"]


class _RootDesignatorsView(Protocol):
    @property
    def judged_object_carrier_reference(self) -> CanonicalReference: ...

    @property
    def evidence_state_carrier_reference(self) -> CanonicalReference: ...

    @property
    def evaluator_carrier_reference(self) -> CanonicalReference: ...


class _DependencyDeclarationView(Protocol):
    @property
    def dependent_reference(self) -> CanonicalReference: ...

    @property
    def dependency_reference(self) -> CanonicalReference: ...

    @property
    def dependency_kind(self) -> object: ...


class _ReferencedSourceBindingView(Protocol):
    @property
    def designator(self) -> ImmutableDesignator: ...

    @property
    def member_reference(self) -> CanonicalReference: ...


class ClaimRecordValidationView(Protocol):
    @property
    def package_identifier(self) -> PackageIdentifier: ...

    @property
    def root_designators(self) -> _RootDesignatorsView: ...

    @property
    def member_inventory(self) -> MemberInventory: ...

    @property
    def dependency_declarations(
        self,
    ) -> tuple[_DependencyDeclarationView, ...]: ...

    @property
    def referenced_sources(self) -> tuple[_ReferencedSourceBindingView, ...]: ...

    @property
    def package_integrity_manifest_member_name(self) -> MemberName: ...

    @property
    def package_integrity_anchor_member_name(self) -> MemberName: ...


def _validate_designated_claim_record_integrity_recovery_member(
    *,
    claim_record: ClaimRecordValidationView,
    member_name,
    expected_role: MemberRole,
    media_type: str,
    schema_designator,
    field_name: str,
) -> None:
    try:
        entry = claim_record.member_inventory.entry_for_name(member_name=member_name)
    except Exception as exc:
        raise ClaimRecordError(
            f"{field_name} must designate a member in the inventory."
        ) from exc
    if entry.member_role is MemberRole.CLAIM_RECORD:
        raise ClaimRecordError(
            f"{field_name} must not designate the claim record itself."
        )
    if entry.member_role is not expected_role:
        raise ClaimRecordError(
            f"{field_name} shall designate the required "
            "claim-record-integrity-recovery member role."
        )
    if entry.classification is not MemberClassification.CLAIM_RECORD_INTEGRITY_RECOVERY:
        raise ClaimRecordError(
            f"{field_name} shall designate claim-record-integrity-recovery "
            "classification."
        )
    if entry.representation.media_type != media_type:
        raise ClaimRecordError(f"{field_name} shall preserve the required media type.")
    if entry.representation.schema_designator != schema_designator:
        raise ClaimRecordError(
            f"{field_name} shall preserve the required schema designator."
        )


def _validate_required_root_entries(*, claim_record: ClaimRecordValidationView) -> None:
    judged_entries = tuple(
        entry
        for entry in claim_record.member_inventory.entries
        if entry.member_role is MemberRole.JUDGED_OBJECT_CARRIER_ROOT
    )
    evidence_entries = tuple(
        entry
        for entry in claim_record.member_inventory.entries
        if entry.member_role is MemberRole.EVIDENCE_STATE_CARRIER_ROOT
    )
    evaluator_entries = tuple(
        entry
        for entry in claim_record.member_inventory.entries
        if entry.member_role is MemberRole.EVALUATOR_CARRIER_ROOT
    )
    if (
        len(judged_entries) != 1
        or len(evidence_entries) != 1
        or len(evaluator_entries) != 1
    ):
        raise RootDesignationError(
            "Exactly one inventory entry shall exist for each required carrier role."
        )
    if (
        judged_entries[0].canonical_reference
        != claim_record.root_designators.judged_object_carrier_reference
    ):
        raise RootDesignationError(
            "Judged-object root designator does not match the inventory."
        )
    if (
        evidence_entries[0].canonical_reference
        != claim_record.root_designators.evidence_state_carrier_reference
    ):
        raise RootDesignationError(
            "Evidence-state root designator does not match the inventory."
        )
    if (
        evaluator_entries[0].canonical_reference
        != claim_record.root_designators.evaluator_carrier_reference
    ):
        raise RootDesignationError(
            "Evaluator root designator does not match the inventory."
        )


def _validate_dependency_declarations(
    *, claim_record: ClaimRecordValidationView
) -> None:
    seen_dependency_pairs: set[
        tuple[CanonicalReference, CanonicalReference, object]
    ] = set()
    for dependency in claim_record.dependency_declarations:
        inventory_dependent = claim_record.member_inventory.entry_for_reference(
            canonical_reference=dependency.dependent_reference
        )
        inventory_target = claim_record.member_inventory.entry_for_reference(
            canonical_reference=dependency.dependency_reference
        )
        if (
            inventory_dependent.classification
            is not MemberClassification.REPLAY_RELEVANT
        ):
            raise DependencyDeclarationError(
                "Dependency declarations shall originate from replay-relevant members."
            )
        if inventory_target.classification is not MemberClassification.REPLAY_RELEVANT:
            raise DependencyDeclarationError(
                "Dependency declarations shall target replay-relevant members."
            )
        if (
            inventory_dependent.member_role is MemberRole.CLAIM_RECORD
            or inventory_target.member_role is MemberRole.CLAIM_RECORD
        ):
            raise DependencyDeclarationError(
                "Claim-record members shall not participate in replay-relevant "
                "dependency declarations."
            )
        dependency_key = (
            dependency.dependent_reference,
            dependency.dependency_reference,
            dependency.dependency_kind,
        )
        if dependency_key in seen_dependency_pairs:
            raise DependencyDeclarationError(
                "Duplicate dependency declarations are not allowed."
            )
        seen_dependency_pairs.add(dependency_key)


def _validate_referenced_sources(*, claim_record: ClaimRecordValidationView) -> None:
    seen_designators: set[ImmutableDesignator] = set()
    seen_member_references: set[CanonicalReference] = set()
    for referenced_source in claim_record.referenced_sources:
        referenced_entry = claim_record.member_inventory.entry_for_reference(
            canonical_reference=referenced_source.member_reference
        )
        if referenced_entry.classification is not MemberClassification.REPLAY_RELEVANT:
            raise ReferencedSourceError(
                "Referenced sources shall resolve to replay-relevant members."
            )
        if referenced_entry.member_role is MemberRole.CLAIM_RECORD:
            raise ReferencedSourceError(
                "The claim record itself shall not stand in for referenced "
                "source material."
            )
        if referenced_source.designator in seen_designators:
            raise ReferencedSourceError(
                "Referenced-source designators shall be unique."
            )
        if referenced_source.member_reference in seen_member_references:
            raise ReferencedSourceError(
                "Each referenced-source binding shall designate a distinct member."
            )
        seen_designators.add(referenced_source.designator)
        seen_member_references.add(referenced_source.member_reference)


def validate_claim_record(*, claim_record: ClaimRecordValidationView) -> None:
    claim_record_entries = tuple(
        entry
        for entry in claim_record.member_inventory.entries
        if entry.member_role is MemberRole.CLAIM_RECORD
    )
    if len(claim_record_entries) != 1:
        raise ClaimRecordError(
            "Exactly one claim-record member shall appear in the member inventory."
        )

    _validate_designated_claim_record_integrity_recovery_member(
        claim_record=claim_record,
        member_name=claim_record.package_integrity_manifest_member_name,
        expected_role=MemberRole.PACKAGE_INTEGRITY_MANIFEST,
        media_type=PACKAGE_INTEGRITY_MANIFEST_MEDIA_TYPE,
        schema_designator=PACKAGE_INTEGRITY_MANIFEST_SCHEMA_DESIGNATOR,
        field_name="package_integrity_manifest_member_name",
    )
    _validate_designated_claim_record_integrity_recovery_member(
        claim_record=claim_record,
        member_name=claim_record.package_integrity_anchor_member_name,
        expected_role=MemberRole.PACKAGE_INTEGRITY_ANCHOR,
        media_type=PACKAGE_INTEGRITY_ANCHOR_MEDIA_TYPE,
        schema_designator=PACKAGE_INTEGRITY_ANCHOR_SCHEMA_DESIGNATOR,
        field_name="package_integrity_anchor_member_name",
    )

    _validate_required_root_entries(claim_record=claim_record)
    _validate_dependency_declarations(claim_record=claim_record)
    _validate_referenced_sources(claim_record=claim_record)
