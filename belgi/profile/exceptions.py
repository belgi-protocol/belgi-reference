"""Profile-layer exception hierarchy."""

from __future__ import annotations

__all__ = [
    "AmbiguousEditionBindingError",
    "EditionError",
    "ExtensionPointError",
    "GovernanceError",
    "InvalidIdentifierError",
    "ProfileError",
    "ProtectedCoreViolationError",
    "UndeclaredExtensionPointError",
    "UnresolvedEditionBindingError",
]


class ProfileError(Exception):
    """Base exception for the profile layer."""


class EditionError(ProfileError):
    """Base exception for exact-edition failures."""


class InvalidIdentifierError(EditionError):
    """Raised when a machine identifier is malformed."""


class UnresolvedEditionBindingError(EditionError):
    """Raised when an exact-edition binding cannot be resolved."""


class AmbiguousEditionBindingError(EditionError):
    """Raised when more than one edition matches one exact-edition binding."""


class ExtensionPointError(ProfileError):
    """Raised when extension-point usage escapes the reserved BELGI surface."""


class GovernanceError(ProfileError):
    """Raised when a governed profile or companion violates Part 3 discipline."""


class ProtectedCoreViolationError(GovernanceError):
    """Raised when a profile or companion tries to reopen protected BELGI meaning."""


class UndeclaredExtensionPointError(GovernanceError):
    """Raised when a profile or companion uses an extension point outside Part 3."""
