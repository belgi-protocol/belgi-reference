"""Deterministic representation-rejection priority."""

from __future__ import annotations

from collections.abc import Iterable

from .model import RepresentationResult, rejected_result

__all__ = ["select_primary_rejection"]

_ORDER = {
    (stage, result_code): (stage_index, code_index)
    for stage_index, (stage, result_codes) in enumerate(
        (
            (1, ("outer-size-exceeded",)),
            (2, ("malformed-container", "unsupported-container-feature")),
            (3, ("entry-count-exceeded",)),
            (
                4,
                (
                    "invalid-entry-name",
                    "unsupported-entry-type",
                    "duplicate-entry",
                    "path-prefix-collision",
                ),
            ),
            (
                5,
                (
                    "member-size-exceeded",
                    "total-size-exceeded",
                    "member-stream-mismatch",
                    "package-mutated-during-read",
                ),
            ),
            (
                6,
                (
                    "missing-claim-record",
                    "claim-record-size-exceeded",
                    "invalid-claim-record-representation",
                ),
            ),
            (7, ("physical-inventory-mismatch", "fixed-role-binding-mismatch")),
        )
    )
    for code_index, result_code in enumerate(result_codes)
}


def select_primary_rejection(
    defects: Iterable[tuple[int, str]],
) -> RepresentationResult:
    materialized = tuple(defects)
    if not materialized:
        raise ValueError("at least one representation defect is required")
    try:
        stage, result_code = min(materialized, key=_ORDER.__getitem__)
    except KeyError as exc:
        raise ValueError("unknown package-representation defect") from exc
    return rejected_result(stage=stage, result_code=result_code)
