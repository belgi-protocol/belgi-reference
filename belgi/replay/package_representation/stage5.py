"""Canonical ZIP Stage-5 preflight, ordering, and terminal counters."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.substrate.io.bounded_zip.exceptions import ZipFailureKind
from belgi.substrate.io.bounded_zip.model import BoundedZipLimits
from belgi.substrate.io.bounded_zip.output import (
    BoundedZipOutputCounters,
    admit_bounded_zip_output,
    preflight_bounded_zip_sizes,
)

__all__ = ["Stage5TraceEntry", "Stage5TraceResult", "evaluate_stage5_trace"]


@dataclass(frozen=True, slots=True, kw_only=True)
class Stage5TraceEntry:
    physical_path: str
    method: str
    declared_uncompressed_octets: int
    produced_octets: int
    stream_complete: bool
    crc_matches: bool
    compressed_boundary_exact: bool

    def raw_path(self) -> bytes:
        try:
            return self.physical_path.encode("ascii", errors="strict")
        except UnicodeEncodeError as exc:
            raise ValueError("Stage-5 trace paths must be raw ASCII text") from exc

    def __post_init__(self) -> None:
        if self.method not in {"STORE", "DEFLATE"}:
            raise ValueError("Stage-5 trace method must be STORE or DEFLATE")
        if self.declared_uncompressed_octets < 0 or self.produced_octets < 0:
            raise ValueError("Stage-5 trace octet counts must be non-negative")


@dataclass(frozen=True, slots=True, kw_only=True)
class Stage5TraceResult:
    accepted: bool
    result_code: str
    processing_order: tuple[str, ...]
    visited_paths: tuple[str, ...]
    member_octets: int
    total_octets: int

    def to_json_object(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "stage": 5,
            "resultCode": self.result_code,
            "processingOrder": list(self.processing_order),
            "visitedPaths": list(self.visited_paths),
            "terminalCounters": {
                "memberOctets": self.member_octets,
                "totalOctets": self.total_octets,
            },
        }


def evaluate_stage5_trace(
    *,
    entries: tuple[Stage5TraceEntry, ...],
    member_maximum: int,
    total_maximum: int,
) -> Stage5TraceResult:
    ordered = tuple(sorted(entries, key=Stage5TraceEntry.raw_path))
    order = tuple(entry.physical_path for entry in ordered)
    limits = BoundedZipLimits(
        archive_bytes=0,
        entry_count=len(entries),
        member_bytes=member_maximum,
        total_member_bytes=total_maximum,
    )
    preflight = preflight_bounded_zip_sizes(
        declared_sizes=tuple(entry.declared_uncompressed_octets for entry in ordered),
        limits=limits,
    )
    if preflight is not None:
        return _trace_result(
            failure_kind=preflight,
            processing_order=order,
            visited_paths=(),
            counters=BoundedZipOutputCounters(member_bytes=0, total_bytes=0),
        )

    visited: list[str] = []
    total_octets = 0
    member_octets = 0
    for entry in ordered:
        visited.append(entry.physical_path)
        admission = admit_bounded_zip_output(
            counters=BoundedZipOutputCounters(
                member_bytes=0,
                total_bytes=total_octets,
            ),
            produced_bytes=entry.produced_octets,
            limits=limits,
        )
        member_octets = admission.counters.member_bytes
        total_octets = admission.counters.total_bytes
        if admission.failure_kind is not None:
            return _trace_result(
                failure_kind=admission.failure_kind,
                processing_order=order,
                visited_paths=tuple(visited),
                counters=admission.counters,
            )
        if (
            entry.produced_octets != entry.declared_uncompressed_octets
            or not entry.stream_complete
            or not entry.crc_matches
            or not entry.compressed_boundary_exact
        ):
            return Stage5TraceResult(
                accepted=False,
                result_code="member-stream-mismatch",
                processing_order=order,
                visited_paths=tuple(visited),
                member_octets=member_octets,
                total_octets=total_octets,
            )
    return Stage5TraceResult(
        accepted=True,
        result_code="stage-5-complete",
        processing_order=order,
        visited_paths=tuple(visited),
        member_octets=member_octets,
        total_octets=total_octets,
    )


def _trace_result(
    *,
    failure_kind: ZipFailureKind,
    processing_order: tuple[str, ...],
    visited_paths: tuple[str, ...],
    counters: BoundedZipOutputCounters,
) -> Stage5TraceResult:
    result_codes = {
        ZipFailureKind.MEMBER_SIZE: "member-size-exceeded",
        ZipFailureKind.TOTAL_SIZE: "total-size-exceeded",
    }
    try:
        result_code = result_codes[failure_kind]
    except KeyError as exc:
        raise ValueError("Stage-5 counters received a non-resource failure") from exc
    return Stage5TraceResult(
        accepted=False,
        result_code=result_code,
        processing_order=processing_order,
        visited_paths=visited_paths,
        member_octets=counters.member_bytes,
        total_octets=counters.total_bytes,
    )
