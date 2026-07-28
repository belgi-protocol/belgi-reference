"""Post-integrity reconciliation for physical ReplayPackageSource values."""

from __future__ import annotations

from belgi.carrier.claim_record import ClaimRecord
from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    FIXED_MEMBER_BINDINGS,
)
from belgi.carrier.package.representation.paths import (
    physical_path_for_logical_path,
)
from belgi.replay.package_representation.exceptions import PackageRepresentationError
from belgi.replay.package_representation.model import (
    RepresentationResult,
    rejected_result,
)
from belgi.replay.package_representation.recovery import (
    AuthenticatedFixedRoleSelectors,
    AuthenticatedMemberBinding,
    AuthenticatedRootReferenceBinding,
    check_recovery_bindings,
)

from .logical_map import LogicalMapReplayPackageSource
from .protocol import PhysicalReplayPackageSource

__all__ = ["require_source_recovery_bindings"]


def require_source_recovery_bindings(
    source: PhysicalReplayPackageSource,
    *,
    claim_record: ClaimRecord,
) -> RepresentationResult:
    envelope = (
        source.resource_envelope
        if isinstance(source, LogicalMapReplayPackageSource)
        else BASELINE_ENVELOPE
    )
    fixed_by_name = {binding.logical_name: binding for binding in FIXED_MEMBER_BINDINGS}
    authenticated_inventory: list[AuthenticatedMemberBinding] = []
    try:
        for entry in claim_record.member_inventory.entries:
            logical_name = str(entry.member_name)
            fixed = fixed_by_name.get(logical_name)
            authenticated_inventory.append(
                AuthenticatedMemberBinding(
                    logical_name=logical_name,
                    physical_path=physical_path_for_logical_path(
                        logical_name,
                        envelope=envelope,
                    ),
                    member_role=entry.member_role.value,
                    classification=entry.classification.value,
                    trusted_json_role=(
                        None if fixed is None else fixed.trusted_json_role
                    ),
                )
            )
    except ValueError as exc:
        raise PackageRepresentationError(
            rejected_result(stage=7, result_code="physical-inventory-mismatch")
        ) from exc
    inventory_by_name = {
        str(entry.member_name): entry for entry in claim_record.member_inventory.entries
    }

    def _fixed_reference(*, logical_name: str) -> str | None:
        entry = inventory_by_name.get(logical_name)
        if entry is None or entry.canonical_reference is None:
            return None
        return str(entry.canonical_reference)

    root_designators = claim_record.root_designators
    selectors = AuthenticatedFixedRoleSelectors(
        package_integrity_manifest_member_name=str(
            claim_record.package_integrity_manifest_member_name
        ),
        package_integrity_anchor_member_name=str(
            claim_record.package_integrity_anchor_member_name
        ),
        root_reference_bindings=(
            AuthenticatedRootReferenceBinding(
                logical_name="judged-object-carrier-root",
                designated_reference=str(
                    root_designators.judged_object_carrier_reference
                ),
                fixed_row_reference=_fixed_reference(
                    logical_name="judged-object-carrier-root"
                ),
            ),
            AuthenticatedRootReferenceBinding(
                logical_name="evidence-state-carrier-root",
                designated_reference=str(
                    root_designators.evidence_state_carrier_reference
                ),
                fixed_row_reference=_fixed_reference(
                    logical_name="evidence-state-carrier-root"
                ),
            ),
            AuthenticatedRootReferenceBinding(
                logical_name="evaluator-carrier-root",
                designated_reference=str(root_designators.evaluator_carrier_reference),
                fixed_row_reference=_fixed_reference(
                    logical_name="evaluator-carrier-root"
                ),
            ),
        ),
    )
    result = check_recovery_bindings(
        claim_record_state="integrity-recovered",
        physical_paths=source.physical_paths,
        authenticated_inventory=authenticated_inventory,
        authenticated_fixed_role_selectors=selectors,
        envelope=envelope,
    )
    if not result.accepted:
        raise PackageRepresentationError(result)
    return result
