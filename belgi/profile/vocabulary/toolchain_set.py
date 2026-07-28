from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.governance import ToolchainSetId

__all__ = [
    "ToolchainComponent",
    "ToolchainSet",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolchainComponent:
    name: str
    identifier: str
    version: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("toolchain component name must not be empty.")
        if not self.identifier:
            raise ValueError("toolchain component identifier must not be empty.")
        if not self.version:
            raise ValueError("toolchain component version must not be empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolchainSet:
    identifier: ToolchainSetId
    components: tuple[ToolchainComponent, ...]

    def __post_init__(self) -> None:
        if not self.components:
            raise ValueError("toolchain set must contain at least one component.")
