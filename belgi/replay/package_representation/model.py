"""Results and logical-member values for package projection."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "LogicalMember",
    "RepresentationResult",
    "accepted_result",
    "rejected_result",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class LogicalMember:
    logical_path: str
    octets: bytes


@dataclass(frozen=True, slots=True, kw_only=True)
class RepresentationResult:
    accepted: bool
    stage: int
    result_code: str
    logical_map: tuple[LogicalMember, ...] | None = None

    def __post_init__(self) -> None:
        if self.accepted != (self.logical_map is not None):
            raise ValueError(
                "accepted representation result must carry one logical member map"
            )


def accepted_result(
    logical_map: tuple[LogicalMember, ...],
    *,
    stage: int = 5,
    result_code: str = "snapshot-established",
) -> RepresentationResult:
    return RepresentationResult(
        accepted=True,
        stage=stage,
        result_code=result_code,
        logical_map=tuple(sorted(logical_map, key=lambda item: item.logical_path)),
    )


def rejected_result(*, stage: int, result_code: str) -> RepresentationResult:
    return RepresentationResult(
        accepted=False,
        stage=stage,
        result_code=result_code,
    )
