"""Step-3d claim-record/anchor target cross-binding."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import MemberName, PackageIdentifier

__all__ = ["IntegrityTargetBindings", "integrity_target_bindings_match"]


@dataclass(frozen=True, slots=True, kw_only=True)
class IntegrityTargetBindings:
    claim_package_identifier: PackageIdentifier
    claim_manifest_member_name: MemberName
    anchor_package_identifier: PackageIdentifier
    anchor_manifest_member_name: MemberName
    consumed_manifest_member_name: MemberName


def integrity_target_bindings_match(*, bindings: IntegrityTargetBindings) -> bool:
    return (
        bindings.anchor_package_identifier == bindings.claim_package_identifier
        and bindings.anchor_manifest_member_name
        == bindings.consumed_manifest_member_name
        and bindings.claim_manifest_member_name
        == bindings.consumed_manifest_member_name
    )
