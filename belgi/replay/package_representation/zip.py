"""ZIP projection into one logical member map without host extraction."""

from __future__ import annotations

from belgi.carrier.package.representation.binding import (
    PackageRepresentationBinding,
    require_selected_binding,
)
from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.carrier.package.representation.paths import (
    logical_path_for_physical_path,
    require_complete_entry_set,
)
from belgi.substrate.io.bounded_zip.exceptions import BoundedZipError, ZipFailureKind
from belgi.substrate.io.bounded_zip.framing import inspect_bounded_zip
from belgi.substrate.io.bounded_zip.model import BoundedZipEntry, BoundedZipLimits
from belgi.substrate.io.bounded_zip.output import preflight_bounded_zip_sizes
from belgi.substrate.io.bounded_zip.stream import read_bounded_zip_entry

from .model import LogicalMember, RepresentationResult, accepted_result, rejected_result

__all__ = ["project_zip_bytes"]


def project_zip_bytes(
    archive_bytes: bytes,
    *,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> RepresentationResult:
    require_selected_binding(selected=selected_binding, supported=supported_binding)
    limits = BoundedZipLimits(
        archive_bytes=envelope.outer_zip_bytes,
        entry_count=envelope.member_count,
        member_bytes=envelope.member_bytes,
        total_member_bytes=envelope.total_member_bytes,
    )
    try:
        archive = inspect_bounded_zip(archive_bytes, limits=limits)
    except BoundedZipError as exc:
        return _zip_error_result(exc)

    validated_entries: list[tuple[BoundedZipEntry, str, str]] = []
    invalid_name = False
    unsupported_type = False
    for entry in archive.entries:
        physical_path = _ascii_name(entry)
        if physical_path is None:
            invalid_name = True
            continue
        try:
            logical_path = logical_path_for_physical_path(
                physical_path,
                envelope=envelope,
            )
        except ValueError:
            invalid_name = True
            continue
        validated_entries.append((entry, physical_path, logical_path))
        if entry.creator_system == 3:
            file_type = (entry.external_attributes >> 16) & 0xF000
            entry_is_regular = (
                file_type == 0x8000 and entry.external_attributes & 0x18 == 0
            )
        elif entry.creator_system == 0:
            entry_is_regular = entry.external_attributes & 0x18 == 0
        else:
            entry_is_regular = False
        if not entry_is_regular:
            unsupported_type = True
    if invalid_name:
        return rejected_result(stage=4, result_code="invalid-entry-name")
    if unsupported_type:
        return rejected_result(stage=4, result_code="unsupported-entry-type")
    physical_paths = [physical_path for _, physical_path, _ in validated_entries]
    if len(set(physical_paths)) != len(physical_paths):
        return rejected_result(stage=4, result_code="duplicate-entry")
    try:
        require_complete_entry_set(tuple(physical_paths))
    except ValueError:
        return rejected_result(stage=4, result_code="path-prefix-collision")

    preflight = preflight_bounded_zip_sizes(
        declared_sizes=tuple(
            entry.uncompressed_size for entry, _, _ in validated_entries
        ),
        limits=limits,
    )
    if preflight is not None:
        return _zip_error_result(BoundedZipError(preflight, "Stage-5 preflight"))

    members: list[LogicalMember] = []
    total_bytes = 0
    for entry, _, logical_path in sorted(
        validated_entries,
        key=lambda item: item[0].name,
    ):
        try:
            read_result = read_bounded_zip_entry(
                archive,
                entry,
                limits=limits,
                total_bytes_before=total_bytes,
            )
        except BoundedZipError as exc:
            return _zip_error_result(exc)
        total_bytes = read_result.total_bytes
        members.append(
            LogicalMember(logical_path=logical_path, octets=read_result.octets)
        )
    return accepted_result(tuple(members))


def _ascii_name(entry: BoundedZipEntry) -> str | None:
    try:
        return entry.name.decode("ascii", errors="strict")
    except UnicodeDecodeError:
        return None


def _zip_error_result(error: BoundedZipError) -> RepresentationResult:
    mapping = {
        ZipFailureKind.OUTER_SIZE: (1, "outer-size-exceeded"),
        ZipFailureKind.MALFORMED: (2, "malformed-container"),
        ZipFailureKind.UNSUPPORTED_FEATURE: (2, "unsupported-container-feature"),
        ZipFailureKind.ENTRY_COUNT: (3, "entry-count-exceeded"),
        ZipFailureKind.MEMBER_SIZE: (5, "member-size-exceeded"),
        ZipFailureKind.TOTAL_SIZE: (5, "total-size-exceeded"),
        ZipFailureKind.STREAM_MISMATCH: (5, "member-stream-mismatch"),
    }
    stage, result_code = mapping[error.kind]
    return rejected_result(stage=stage, result_code=result_code)
