"""Portable logical paths and their physical member mapping."""

from __future__ import annotations

import re

from .contract import BASELINE_ENVELOPE, PackageResourceEnvelope

__all__ = [
    "logical_path_for_physical_path",
    "physical_path_for_logical_path",
    "require_complete_entry_set",
    "require_portable_logical_path",
]

_SEGMENT = re.compile(r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?")
_RESERVED_BASENAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


def require_portable_logical_path(
    logical_path: str,
    *,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> str:
    try:
        encoded = logical_path.encode("ascii", errors="strict")
    except UnicodeEncodeError as exc:
        raise ValueError("logical member path must contain ASCII text only") from exc
    if not 1 <= len(encoded) <= envelope.path_bytes:
        raise ValueError("logical member path exceeds its byte envelope")
    if logical_path.startswith("/") or logical_path.endswith("/"):
        raise ValueError("logical member path must be relative and name a file")
    segments = logical_path.split("/")
    if not 1 <= len(segments) <= envelope.path_segments:
        raise ValueError("logical member path exceeds its segment envelope")
    for segment in segments:
        segment_bytes = segment.encode("ascii")
        if not 1 <= len(segment_bytes) <= envelope.path_segment_bytes:
            raise ValueError("logical member path segment exceeds its byte envelope")
        if _SEGMENT.fullmatch(segment) is None:
            raise ValueError("logical member path contains a non-portable segment")
        if segment in {".", ".."} or segment.split(".", 1)[0] in (_RESERVED_BASENAMES):
            raise ValueError("logical member path contains a reserved segment")
    return logical_path


def physical_path_for_logical_path(
    logical_path: str,
    *,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> str:
    require_portable_logical_path(logical_path, envelope=envelope)
    if logical_path == "claim-record.json":
        raise ValueError("logical member path claim-record.json is reserved")
    if logical_path == "claim-record":
        return "claim-record.json"
    return logical_path


def logical_path_for_physical_path(
    physical_path: str,
    *,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> str:
    if physical_path == "claim-record.json":
        return "claim-record"
    if physical_path == "claim-record":
        raise ValueError("physical member path claim-record is reserved")
    require_portable_logical_path(physical_path, envelope=envelope)
    return physical_path


def require_complete_entry_set(paths: tuple[str, ...]) -> None:
    if len(set(paths)) != len(paths):
        raise ValueError("physical package contains a duplicate entry")
    path_set = set(paths)
    for path in paths:
        components = path.split("/")
        for component_count in range(1, len(components)):
            prefix = "/".join(components[:component_count])
            if prefix in path_set:
                raise ValueError("physical package contains a path-prefix collision")
