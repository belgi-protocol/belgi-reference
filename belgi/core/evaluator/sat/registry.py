from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from belgi.core.evaluator.exceptions import (
    DuplicateSatRegistrationError,
    SatRegistryError,
)
from belgi.core.evaluator.model import SemanticsKey

from .protocol import Sat

__all__ = ["SatRegistration", "SatRegistry"]


@dataclass(frozen=True, slots=True, kw_only=True)
class SatRegistration:
    semantics_key: SemanticsKey
    sat: Sat
    provider_witnesses: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.semantics_key, str) or not self.semantics_key.strip():
            raise SatRegistryError(
                "SatRegistration semantics_key must be a non-empty string."
            )
        if not callable(self.sat):
            raise SatRegistryError("SatRegistration sat must be callable.")
        object.__setattr__(self, "provider_witnesses", tuple(self.provider_witnesses))
        _validate_provider_witnesses(
            semantics_key=self.semantics_key,
            sat=self.sat,
            provider_witnesses=self.provider_witnesses,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SatRegistry:
    _handlers: Mapping[SemanticsKey, Sat] = field(default_factory=dict, repr=False)
    _provider_witnesses: Mapping[SemanticsKey, tuple[object, ...]] = field(
        default_factory=dict,
        repr=False,
    )

    def __post_init__(self) -> None:
        normalized: dict[SemanticsKey, Sat] = {}
        for semantics_key, sat in self._handlers.items():
            if not isinstance(semantics_key, str) or not semantics_key.strip():
                raise SatRegistryError(
                    "SatRegistry semantics keys must be non-empty strings."
                )
            if not callable(sat):
                raise SatRegistryError("SatRegistry handlers must be callable.")
            if semantics_key in normalized:
                raise DuplicateSatRegistrationError(
                    f"Duplicate Sat registration for semantics_key: {semantics_key}.",
                )
            normalized[semantics_key] = sat
        ordered = {
            semantics_key: normalized[semantics_key]
            for semantics_key in sorted(normalized, key=str)
        }
        provider_witnesses: dict[SemanticsKey, tuple[object, ...]] = {}
        for semantics_key, witnesses in self._provider_witnesses.items():
            if semantics_key not in normalized:
                raise SatRegistryError(
                    "SatRegistry provider witness references unknown semantics_key: "
                    f"{semantics_key}."
                )
            witness_tuple = tuple(witnesses)
            _validate_provider_witnesses(
                semantics_key=semantics_key,
                sat=normalized[semantics_key],
                provider_witnesses=witness_tuple,
            )
            if witness_tuple:
                provider_witnesses[semantics_key] = witness_tuple
        ordered_provider_witnesses = {
            semantics_key: provider_witnesses[semantics_key]
            for semantics_key in sorted(provider_witnesses, key=str)
        }
        object.__setattr__(self, "_handlers", MappingProxyType(ordered))
        object.__setattr__(
            self,
            "_provider_witnesses",
            MappingProxyType(ordered_provider_witnesses),
        )

    @classmethod
    def empty(cls) -> SatRegistry:
        return cls()

    @classmethod
    def from_registrations(
        cls,
        *,
        registrations: tuple[SatRegistration, ...],
    ) -> SatRegistry:
        handlers: dict[SemanticsKey, Sat] = {}
        provider_witnesses: dict[SemanticsKey, tuple[object, ...]] = {}
        for registration in registrations:
            if registration.semantics_key in handlers:
                raise DuplicateSatRegistrationError(
                    "Duplicate Sat registration for semantics_key: "
                    f"{registration.semantics_key}.",
                )
            handlers[registration.semantics_key] = registration.sat
            if registration.provider_witnesses:
                provider_witnesses[registration.semantics_key] = (
                    registration.provider_witnesses
                )
        return cls(_handlers=handlers, _provider_witnesses=provider_witnesses)

    @property
    def registered_keys(self) -> tuple[SemanticsKey, ...]:
        return tuple(self._handlers.keys())

    def resolve(self, *, semantics_key: SemanticsKey | None) -> Sat | None:
        if semantics_key is None:
            return None
        return self._handlers.get(semantics_key)

    def provider_witnesses_for(
        self, *, semantics_key: SemanticsKey | None
    ) -> tuple[object, ...]:
        if semantics_key is None:
            return ()
        return self._provider_witnesses.get(semantics_key, ())

    def provider_witnesses(self) -> tuple[object, ...]:
        return tuple(
            witness
            for semantics_key in self.registered_keys
            for witness in self.provider_witnesses_for(semantics_key=semantics_key)
        )

    def with_registration(
        self,
        *,
        registration: SatRegistration,
        replace: bool = False,
    ) -> SatRegistry:
        if not replace and registration.semantics_key in self._handlers:
            raise DuplicateSatRegistrationError(
                "Duplicate Sat registration for semantics_key: "
                f"{registration.semantics_key}.",
            )
        updated = dict(self._handlers)
        updated[registration.semantics_key] = registration.sat
        updated_provider_witnesses = dict(self._provider_witnesses)
        if registration.provider_witnesses:
            updated_provider_witnesses[registration.semantics_key] = (
                registration.provider_witnesses
            )
        else:
            updated_provider_witnesses.pop(registration.semantics_key, None)
        return SatRegistry(
            _handlers=updated,
            _provider_witnesses=updated_provider_witnesses,
        )

    def with_registrations(
        self,
        *,
        registrations: tuple[SatRegistration, ...],
        replace: bool = False,
    ) -> SatRegistry:
        updated = self
        for registration in registrations:
            updated = updated.with_registration(
                registration=registration,
                replace=replace,
            )
        return updated


def _validate_provider_witnesses(
    *,
    semantics_key: SemanticsKey,
    sat: Sat,
    provider_witnesses: tuple[object, ...],
) -> None:
    observed_entrypoint = getattr(sat, "__belgi_provider_entrypoint__", None)
    for witness in provider_witnesses:
        witness_semantics_key = getattr(witness, "semantics_key", None)
        if witness_semantics_key != semantics_key:
            raise SatRegistryError(
                "SatRegistration provider witness semantics_key must match "
                "the registered semantics_key."
            )
        expected_entrypoint = getattr(witness, "callable_entrypoint", None)
        if not isinstance(expected_entrypoint, str) or not expected_entrypoint:
            raise SatRegistryError(
                "SatRegistration provider witness callable entrypoint must be text."
            )
        if not isinstance(observed_entrypoint, str) or not observed_entrypoint:
            raise SatRegistryError(
                "SatRegistration with provider witnesses must expose the "
                "registered Sat handler entrypoint."
            )
        if observed_entrypoint != expected_entrypoint:
            raise SatRegistryError(
                "SatRegistration provider witness callable entrypoint must match "
                "the registered Sat handler."
            )
