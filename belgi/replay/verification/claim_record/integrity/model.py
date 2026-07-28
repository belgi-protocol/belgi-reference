from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import CanonicalReference, MemberName

__all__ = ["ClaimRecordIntegrityRecovery"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimRecordIntegrityRecovery:
    claim_record_member_name: MemberName
    claim_record_reference: CanonicalReference
    manifest_member_name: MemberName
    anchor_member_name: MemberName
