from __future__ import annotations

from belgi.carrier import MemberInventoryEntry
from belgi.replay.lifting.exceptions import PackageReadError
from belgi.replay.lifting.model import ResolvedPackageMember
from belgi.replay.package_source.protocol import ReplayPackageSource

__all__ = ["read_member_bytes", "resolve_package_member"]


def read_member_bytes(
    *,
    package: ReplayPackageSource,
    member: MemberInventoryEntry,
) -> bytes:
    try:
        return package.read_member(inventory_entry=member)
    except Exception as exc:
        raise PackageReadError(
            f"Could not read package member {member.member_name!r} as preserved.",
        ) from exc


def resolve_package_member(
    *,
    package: ReplayPackageSource,
    inventory_entry: MemberInventoryEntry,
) -> ResolvedPackageMember:
    try:
        package_member = package.package_member(inventory_entry=inventory_entry)
    except Exception as exc:
        raise PackageReadError(
            f"Could not resolve package member {inventory_entry.member_name!r}.",
        ) from exc
    return ResolvedPackageMember(
        inventory_entry=inventory_entry,
        package_member=package_member,
    )
