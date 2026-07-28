"""Authenticated physical-inventory and fixed-role reconciliation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    FIXED_MEMBER_BINDINGS,
    PackageResourceEnvelope,
)
from belgi.carrier.package.representation.paths import (
    physical_path_for_logical_path,
)

from .model import RepresentationResult, accepted_result, rejected_result

__all__ = [
    "AuthenticatedFixedRoleSelectors",
    "AuthenticatedMemberBinding",
    "AuthenticatedRootReferenceBinding",
    "check_recovery_bindings",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthenticatedMemberBinding:
    logical_name: str
    physical_path: str
    member_role: str
    classification: str
    trusted_json_role: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthenticatedRootReferenceBinding:
    logical_name: str
    designated_reference: str
    fixed_row_reference: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthenticatedFixedRoleSelectors:
    package_integrity_manifest_member_name: str
    package_integrity_anchor_member_name: str
    root_reference_bindings: tuple[AuthenticatedRootReferenceBinding, ...]


def check_recovery_bindings(
    *,
    claim_record_state: str,
    physical_paths: Iterable[str],
    authenticated_inventory: Iterable[AuthenticatedMemberBinding],
    authenticated_fixed_role_selectors: AuthenticatedFixedRoleSelectors | None = None,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> RepresentationResult:
    physical = tuple(physical_paths)
    inventory = tuple(authenticated_inventory)
    if claim_record_state == "missing" or "claim-record.json" not in physical:
        return rejected_result(stage=6, result_code="missing-claim-record")
    if claim_record_state != "integrity-recovered":
        return rejected_result(
            stage=6,
            result_code="invalid-claim-record-representation",
        )
    inventory_physical = tuple(binding.physical_path for binding in inventory)
    inventory_logical = tuple(binding.logical_name for binding in inventory)
    if (
        len(set(physical)) != len(physical)
        or len(set(inventory_physical)) != len(inventory_physical)
        or len(set(inventory_logical)) != len(inventory_logical)
        or set(physical) != set(inventory_physical)
    ):
        return rejected_result(stage=7, result_code="physical-inventory-mismatch")
    expected = tuple(
        AuthenticatedMemberBinding(
            logical_name=binding.logical_name,
            physical_path=binding.physical_path,
            member_role=binding.member_role,
            classification=binding.classification,
            trusted_json_role=binding.trusted_json_role,
        )
        for binding in FIXED_MEMBER_BINDINGS
    )
    fixed_names = {binding.logical_name for binding in expected}
    for binding in inventory:
        try:
            projected_path = physical_path_for_logical_path(
                binding.logical_name,
                envelope=envelope,
            )
        except ValueError:
            return rejected_result(stage=7, result_code="physical-inventory-mismatch")
        if binding.physical_path != projected_path:
            result_code = (
                "fixed-role-binding-mismatch"
                if binding.logical_name in fixed_names
                else "physical-inventory-mismatch"
            )
            return rejected_result(stage=7, result_code=result_code)
    by_logical_name = {binding.logical_name: binding for binding in inventory}
    if any(
        by_logical_name.get(binding.logical_name) != binding for binding in expected
    ):
        return rejected_result(stage=7, result_code="fixed-role-binding-mismatch")
    if authenticated_fixed_role_selectors is not None:
        selectors = authenticated_fixed_role_selectors
        if (
            selectors.package_integrity_manifest_member_name
            != "package-integrity-manifest"
            or selectors.package_integrity_anchor_member_name
            != "package-integrity-anchor"
        ):
            return rejected_result(stage=7, result_code="fixed-role-binding-mismatch")
        expected_root_names = {
            "judged-object-carrier-root",
            "evidence-state-carrier-root",
            "evaluator-carrier-root",
        }
        root_bindings = selectors.root_reference_bindings
        if {
            binding.logical_name for binding in root_bindings
        } != expected_root_names or any(
            binding.fixed_row_reference is None
            or binding.designated_reference != binding.fixed_row_reference
            for binding in root_bindings
        ):
            return rejected_result(stage=7, result_code="fixed-role-binding-mismatch")
    return accepted_result((), stage=8, result_code="complete")
