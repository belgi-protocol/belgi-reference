"""Verifier-side replay-package source port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from belgi.carrier.inventory import (
    MemberInventoryEntry,
    MemberName,
    PackageMember,
)

__all__ = [
    "PhysicalReplayPackageSource",
    "ReplayPackageSource",
]


class ReplayPackageSource(Protocol):
    def claim_record_bytes(self) -> bytes: ...

    def has_bootstrap_member(self, *, member_name: MemberName) -> bool: ...

    def read_bootstrap_member(self, *, member_name: MemberName) -> bytes: ...

    def has_member(self, *, inventory_entry: MemberInventoryEntry) -> bool: ...

    def read_member(self, *, inventory_entry: MemberInventoryEntry) -> bytes: ...

    def package_member(
        self,
        *,
        inventory_entry: MemberInventoryEntry,
    ) -> PackageMember: ...


@runtime_checkable
class PhysicalReplayPackageSource(ReplayPackageSource, Protocol):
    @property
    def physical_paths(self) -> tuple[str, ...]: ...
