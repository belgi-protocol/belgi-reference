"""Read-only substrate I/O used by the public reference distribution."""

from __future__ import annotations

from .access import (
    directory_supports_state_writes,
    file_supports_state_writes,
    filesystem_ignores_case,
    lexical_absolute_path,
    paths_share_filesystem_identity,
)
from .exceptions import RootedPathSymlinkError
from .jcs import canonicalize_jcs
from .json.encoding import (
    canonical_json_bytes,
    canonical_json_text,
    render_json_bytes,
    render_json_text,
)
from .json.files import load_json_object, load_json_value
from .json.parsing import (
    parse_json_object,
    parse_json_object_with_duplicate_tracking,
    parse_json_value,
    require_no_duplicate_json_keys,
)
from .json.values import freeze_json_compatible_value
from .path_presentation import render_filesystem_path
from .rooted_snapshot.api import (
    RootedDirectorySnapshot,
    RootedPathAbsenceSnapshot,
    open_binary_file_snapshot,
    open_directory_snapshot,
    open_path_absence_snapshot,
    rooted_regular_file_supports_state_writes,
)
from .strict_json import JSONDomainError, JSONValidationStage, decode_strict_json

__all__ = [
    "JSONDomainError",
    "JSONValidationStage",
    "RootedDirectorySnapshot",
    "RootedPathAbsenceSnapshot",
    "RootedPathSymlinkError",
    "canonical_json_bytes",
    "canonical_json_text",
    "canonicalize_jcs",
    "decode_strict_json",
    "directory_supports_state_writes",
    "file_supports_state_writes",
    "filesystem_ignores_case",
    "freeze_json_compatible_value",
    "lexical_absolute_path",
    "load_json_object",
    "load_json_value",
    "open_binary_file_snapshot",
    "open_directory_snapshot",
    "open_path_absence_snapshot",
    "parse_json_object",
    "parse_json_object_with_duplicate_tracking",
    "parse_json_value",
    "paths_share_filesystem_identity",
    "render_filesystem_path",
    "render_json_bytes",
    "render_json_text",
    "require_no_duplicate_json_keys",
    "rooted_regular_file_supports_state_writes",
]
