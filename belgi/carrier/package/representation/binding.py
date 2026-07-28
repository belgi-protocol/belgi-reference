"""Trusted package-representation procedure selection."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.inventory import ImmutableDesignator

__all__ = ["PackageRepresentationBinding", "require_selected_binding"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageRepresentationBinding:
    procedure_identifier: str
    defining_source: ImmutableDesignator

    def __post_init__(self) -> None:
        if self.procedure_identifier == "" or self.procedure_identifier.strip() != (
            self.procedure_identifier
        ):
            raise ValueError(
                "package-representation procedure identifier must be exact non-empty text"
            )


def require_selected_binding(
    *,
    selected: PackageRepresentationBinding,
    supported: PackageRepresentationBinding,
) -> None:
    if selected != supported:
        raise ValueError(
            "selected package-representation procedure or defining source is unsupported"
        )
