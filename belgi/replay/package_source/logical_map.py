"""ReplayPackageSource backed by one admitted logical member map."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.claim_record import (
    ClaimRecord,
    parse_claim_record_bytes_for_replay_read,
)
from belgi.carrier.inventory import (
    MemberClassification,
    MemberError,
    MemberInventoryEntry,
    MemberName,
    PackageMember,
)
from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.carrier.package.representation.paths import (
    physical_path_for_logical_path,
)
from belgi.carrier.projection import compute_projection
from belgi.replay.package_representation.exceptions import PackageRepresentationError
from belgi.replay.package_representation.model import (
    LogicalMember,
    RepresentationResult,
    rejected_result,
)
from belgi.substrate.io import JSONDomainError, decode_strict_json

from .exceptions import PackageSourceMemberNotFoundError
from .protocol import ReplayPackageSource

__all__ = [
    "LogicalMapReplayPackageSource",
    "claim_record_projection_rejection",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class LogicalMapReplayPackageSource(ReplayPackageSource):
    members: tuple[LogicalMember, ...]
    physical_paths: tuple[str, ...]
    resource_envelope: PackageResourceEnvelope = BASELINE_ENVELOPE

    def __post_init__(self) -> None:
        logical_paths = tuple(member.logical_path for member in self.members)
        if len(set(logical_paths)) != len(logical_paths):
            raise ValueError("logical replay-package source contains duplicate members")
        if len(set(self.physical_paths)) != len(self.physical_paths):
            raise ValueError("logical replay-package source contains duplicate paths")
        expected_physical_paths = tuple(
            physical_path_for_logical_path(
                logical_path,
                envelope=self.resource_envelope,
            )
            for logical_path in logical_paths
        )
        if self.physical_paths != expected_physical_paths:
            raise ValueError(
                "logical replay-package source paths differ from their exact projection"
            )

    @classmethod
    def from_projection(
        cls,
        *,
        members: tuple[LogicalMember, ...],
        envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
    ) -> LogicalMapReplayPackageSource:
        rejection = claim_record_projection_rejection(
            members=members,
            envelope=envelope,
        )
        if rejection is not None:
            raise PackageRepresentationError(rejection)
        return cls(
            members=members,
            physical_paths=tuple(
                physical_path_for_logical_path(
                    member.logical_path,
                    envelope=envelope,
                )
                for member in members
            ),
            resource_envelope=envelope,
        )

    def logical_member_names(self) -> tuple[str, ...]:
        return tuple(member.logical_path for member in self.members)

    def claim_record_bytes(self) -> bytes:
        return self._member_octets(logical_path="claim-record")

    def has_bootstrap_member(self, *, member_name: MemberName) -> bool:
        try:
            self._member_octets(logical_path=str(member_name))
        except KeyError:
            return False
        return True

    def read_bootstrap_member(self, *, member_name: MemberName) -> bytes:
        return self._member_octets(logical_path=str(member_name))

    def has_member(self, *, inventory_entry: MemberInventoryEntry) -> bool:
        claim_record = self._claim_record()
        try:
            expected = self._validated_inventory_entry(
                inventory_entry=inventory_entry,
                claim_record=claim_record,
            )
            self._member_octets(logical_path=str(expected.member_name))
        except (KeyError, MemberError, PackageSourceMemberNotFoundError):
            return False
        return True

    def read_member(self, *, inventory_entry: MemberInventoryEntry) -> bytes:
        expected = self._validated_inventory_entry(inventory_entry=inventory_entry)
        return self._member_octets(logical_path=str(expected.member_name))

    def package_member(self, *, inventory_entry: MemberInventoryEntry) -> PackageMember:
        expected = self._validated_inventory_entry(inventory_entry=inventory_entry)
        preserved_bytes = self._member_octets(logical_path=str(expected.member_name))
        if expected.classification is MemberClassification.REPLAY_RELEVANT:
            if expected.projection_rule_designator is not None:
                raise ValueError(
                    "physical package source supports exact-preserved-octets members only"
                )
            return PackageMember(
                member_name=expected.member_name,
                member_role=expected.member_role,
                representation=expected.representation,
                preserved_bytes=preserved_bytes,
                classification=expected.classification,
                canonical_reference=expected.canonical_reference,
                projection=compute_projection(
                    preserved_bytes=preserved_bytes,
                    projection_spec=None,
                ),
            )
        return PackageMember(
            member_name=expected.member_name,
            member_role=expected.member_role,
            representation=expected.representation,
            preserved_bytes=preserved_bytes,
            classification=expected.classification,
            canonical_reference=None,
            projection=None,
        )

    def _claim_record(self) -> ClaimRecord:
        return parse_claim_record_bytes_for_replay_read(
            claim_record_bytes=self.claim_record_bytes()
        )

    def _validated_inventory_entry(
        self,
        *,
        inventory_entry: MemberInventoryEntry,
        claim_record: ClaimRecord | None = None,
    ) -> MemberInventoryEntry:
        source_claim_record = claim_record or self._claim_record()
        expected = source_claim_record.member_inventory.entry_for_name(
            member_name=inventory_entry.member_name
        )
        if expected != inventory_entry:
            raise PackageSourceMemberNotFoundError(
                "physical replay-package inventory entry differs from the claim record"
            )
        return expected

    def _member_octets(self, *, logical_path: str) -> bytes:
        for member in self.members:
            if member.logical_path == logical_path:
                return member.octets
        raise KeyError(f"replay-package logical member is missing: {logical_path}")


def _require_claim_record(
    members: tuple[LogicalMember, ...],
    *,
    envelope: PackageResourceEnvelope,
) -> bytes:
    claim_records = tuple(
        member for member in members if member.logical_path == "claim-record"
    )
    if not claim_records:
        raise PackageRepresentationError(
            rejected_result(stage=6, result_code="missing-claim-record")
        )
    claim_record_octets = claim_records[0].octets
    if len(claim_record_octets) > envelope.claim_record_bytes:
        raise PackageRepresentationError(
            rejected_result(stage=6, result_code="claim-record-size-exceeded")
        )
    return claim_record_octets


def claim_record_projection_rejection(
    *,
    members: tuple[LogicalMember, ...],
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> RepresentationResult | None:
    """Validate Stage 6 over one already-established Stage-5 snapshot."""

    try:
        claim_record_octets = _require_claim_record(members, envelope=envelope)
        decode_strict_json(
            claim_record_octets,
            maximum_depth=envelope.claim_record_json_nesting_depth,
        )
    except PackageRepresentationError as exc:
        return exc.result
    except JSONDomainError:
        return rejected_result(
            stage=6,
            result_code="invalid-claim-record-representation",
        )
    return None
