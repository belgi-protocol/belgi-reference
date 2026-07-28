from __future__ import annotations

from belgi.profile.governance import BindingKindId

__all__ = [
    "ALL_BINDING_KINDS",
    "REFUTES",
    "SATISFIES",
    "SUPPORTS",
]


SATISFIES = BindingKindId("belgi.software-change.binding.satisfies")
SUPPORTS = BindingKindId("belgi.software-change.binding.supports")
REFUTES = BindingKindId("belgi.software-change.binding.refutes")

ALL_BINDING_KINDS: tuple[BindingKindId, ...] = (
    SATISFIES,
    SUPPORTS,
    REFUTES,
)
