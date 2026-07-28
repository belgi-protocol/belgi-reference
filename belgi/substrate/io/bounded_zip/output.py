"""Overflow-safe counters shared by bounded ZIP Stage-5 consumers."""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import ZipFailureKind
from .model import BoundedZipLimits

__all__ = [
    "BoundedZipOutputAdmission",
    "BoundedZipOutputCounters",
    "admit_bounded_zip_output",
    "preflight_bounded_zip_sizes",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundedZipOutputCounters:
    member_bytes: int
    total_bytes: int


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundedZipOutputAdmission:
    counters: BoundedZipOutputCounters
    failure_kind: ZipFailureKind | None


def preflight_bounded_zip_sizes(
    *, declared_sizes: tuple[int, ...], limits: BoundedZipLimits
) -> ZipFailureKind | None:
    if any(size < 0 for size in declared_sizes):
        raise ValueError("declared ZIP output sizes must be non-negative")
    if any(size > limits.member_bytes for size in declared_sizes):
        return ZipFailureKind.MEMBER_SIZE
    aggregate = 0
    for size in declared_sizes:
        if size > limits.total_member_bytes - aggregate:
            return ZipFailureKind.TOTAL_SIZE
        aggregate += size
    return None


def admit_bounded_zip_output(
    *,
    counters: BoundedZipOutputCounters,
    produced_bytes: int,
    limits: BoundedZipLimits,
) -> BoundedZipOutputAdmission:
    if produced_bytes < 0:
        raise ValueError("produced ZIP output count must be non-negative")
    if not 0 <= counters.member_bytes <= limits.member_bytes:
        raise ValueError("member output counter is outside its envelope")
    if not 0 <= counters.total_bytes <= limits.total_member_bytes:
        raise ValueError("aggregate output counter is outside its envelope")
    member_remaining = limits.member_bytes - counters.member_bytes
    total_remaining = limits.total_member_bytes - counters.total_bytes
    admitted = min(produced_bytes, member_remaining, total_remaining)
    updated = BoundedZipOutputCounters(
        member_bytes=counters.member_bytes + admitted,
        total_bytes=counters.total_bytes + admitted,
    )
    if admitted == produced_bytes:
        return BoundedZipOutputAdmission(counters=updated, failure_kind=None)
    failure_kind = (
        ZipFailureKind.MEMBER_SIZE
        if member_remaining <= total_remaining
        else ZipFailureKind.TOTAL_SIZE
    )
    return BoundedZipOutputAdmission(
        counters=updated,
        failure_kind=failure_kind,
    )
