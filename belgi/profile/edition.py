from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import NewType, TypeAlias
from urllib.parse import urlparse

from .exceptions import (
    AmbiguousEditionBindingError as _AmbiguousEditionBindingError,
)
from .exceptions import InvalidIdentifierError as _InvalidIdentifierError
from .exceptions import (
    UnresolvedEditionBindingError as _UnresolvedEditionBindingError,
)

__all__ = [
    "CompanionIdentifier",
    "Digest",
    "EditionCatalog",
    "EditionFamilyIdentifier",
    "EditionKind",
    "ExactEdition",
    "ExactEditionBinding",
    "ImmutableDesignator",
    "ProfileIdentifier",
    "PublisherIdentifier",
    "VersionDesignator",
    "companion_edition",
    "companion_edition_binding",
    "external_edition",
    "external_edition_binding",
    "is_controlled_belgi_edition_family_identifier",
    "profile_edition",
    "profile_edition_binding",
    "resolve_exact_edition",
]


ProfileIdentifier = NewType("ProfileIdentifier", str)
CompanionIdentifier = NewType("CompanionIdentifier", str)
VersionDesignator = NewType("VersionDesignator", str)
PublisherIdentifier = NewType("PublisherIdentifier", str)
EditionFamilyIdentifier: TypeAlias = ProfileIdentifier | CompanionIdentifier | str

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DIGEST_VALUE_PATTERN = re.compile(r"^[0-9A-Fa-f]+$")
_CONTROLLED_FAMILY_IDENTIFIER_PREFIX = "https://belgi.dev/ids/"
_CONTROLLED_FAMILY_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._~-]*$")


class EditionKind(str, Enum):
    PROFILE = "profile"
    COMPANION = "companion"
    EXTERNAL = "external"


def _require_machine_identifier(*, value: str, field_name: str) -> str:
    if not value:
        raise _InvalidIdentifierError(f"{field_name} must not be empty.")
    if not _IDENTIFIER_PATTERN.match(value):
        raise _InvalidIdentifierError(
            f"{field_name} must match {_IDENTIFIER_PATTERN.pattern!r}: {value!r}."
        )
    return value


def is_controlled_belgi_edition_family_identifier(*, value: str) -> bool:
    if not value.startswith(_CONTROLLED_FAMILY_IDENTIFIER_PREFIX):
        return False
    parsed = urlparse(value)
    path_suffix = parsed.path.removeprefix("/ids/")
    return (
        parsed.scheme == "https"
        and parsed.netloc == "belgi.dev"
        and parsed.path.startswith("/ids/")
        and bool(path_suffix)
        and all(
            segment not in {".", ".."}
            and _CONTROLLED_FAMILY_SEGMENT_PATTERN.fullmatch(segment) is not None
            for segment in path_suffix.split("/")
        )
        and not parsed.params
        and not parsed.query
        and not parsed.fragment
    )


def _require_edition_family_identifier(*, value: str) -> str:
    if value.startswith(_CONTROLLED_FAMILY_IDENTIFIER_PREFIX):
        if is_controlled_belgi_edition_family_identifier(value=value):
            return value
        raise _InvalidIdentifierError(
            "controlled family_identifier must be one absolute "
            "https://belgi.dev/ids/... identifier without parameters, query, "
            f"or fragment: {value!r}."
        )
    return _require_machine_identifier(
        value=value,
        field_name="family_identifier",
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class Digest:
    algorithm_id: str
    digest_value: str

    def __post_init__(self) -> None:
        _require_machine_identifier(
            value=self.algorithm_id,
            field_name="algorithm_id",
        )
        if not self.digest_value:
            raise _InvalidIdentifierError("digest_value must not be empty.")
        if not _DIGEST_VALUE_PATTERN.match(self.digest_value):
            raise _InvalidIdentifierError(
                "digest_value must be a hexadecimal octet string."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class ImmutableDesignator:
    uri: str
    digest: Digest

    def __post_init__(self) -> None:
        parsed = urlparse(self.uri)
        if not parsed.scheme:
            raise _InvalidIdentifierError(
                f"immutable-designator URI must be absolute: {self.uri!r}."
            )
        if parsed.scheme in {"http", "https"} and not parsed.netloc:
            raise _InvalidIdentifierError(
                f"immutable-designator URI must include an authority: {self.uri!r}."
            )

    @property
    def stable_key(self) -> tuple[str, str, str]:
        return (self.uri, self.digest.algorithm_id, self.digest.digest_value)

    def __str__(self) -> str:
        return f"{self.uri}#{self.digest.algorithm_id}:{self.digest.digest_value}"


@dataclass(frozen=True, slots=True, kw_only=True)
class ExactEditionBinding:
    kind: EditionKind
    family_identifier: EditionFamilyIdentifier
    version_designator: VersionDesignator
    immutable_designator: ImmutableDesignator

    def __post_init__(self) -> None:
        _require_edition_family_identifier(value=str(self.family_identifier))
        _require_machine_identifier(
            value=str(self.version_designator),
            field_name="version_designator",
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ExactEdition(ExactEditionBinding):
    title: str
    scope: str
    owning_publisher: PublisherIdentifier

    def __post_init__(self) -> None:
        ExactEditionBinding.__post_init__(self)
        if not self.title:
            raise _InvalidIdentifierError("title must not be empty.")
        if not self.scope:
            raise _InvalidIdentifierError("scope must not be empty.")
        _require_machine_identifier(
            value=str(self.owning_publisher),
            field_name="owning_publisher",
        )

    @property
    def binding(self) -> ExactEditionBinding:
        return ExactEditionBinding(
            kind=self.kind,
            family_identifier=self.family_identifier,
            version_designator=self.version_designator,
            immutable_designator=self.immutable_designator,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class EditionCatalog:
    editions: tuple[ExactEdition, ...]

    def __post_init__(self) -> None:
        seen_designators: set[tuple[str, str, str]] = set()
        seen_family_versions: set[tuple[str, str]] = set()
        for edition in self.editions:
            designator_key = edition.immutable_designator.stable_key
            family_version_key = (
                str(edition.family_identifier),
                str(edition.version_designator),
            )
            if designator_key in seen_designators:
                raise _AmbiguousEditionBindingError(
                    "duplicate immutable designator in EditionCatalog: "
                    f"{edition.immutable_designator!s}."
                )
            if family_version_key in seen_family_versions:
                raise _AmbiguousEditionBindingError(
                    "duplicate family/version in EditionCatalog: "
                    f"{family_version_key[0]!r}@{family_version_key[1]!r}."
                )
            seen_designators.add(designator_key)
            seen_family_versions.add(family_version_key)

    def resolve(self, *, binding: ExactEditionBinding) -> ExactEdition:
        matches = tuple(
            edition
            for edition in self.editions
            if edition.kind == binding.kind
            and str(edition.family_identifier) == str(binding.family_identifier)
            and str(edition.version_designator) == str(binding.version_designator)
            and edition.immutable_designator == binding.immutable_designator
        )
        if not matches:
            raise _UnresolvedEditionBindingError(
                "no exact edition matched binding "
                f"{binding.family_identifier!r}@{binding.version_designator!r}."
            )
        if len(matches) != 1:
            raise _AmbiguousEditionBindingError(
                "multiple exact editions matched one exact binding for "
                f"{binding.family_identifier!r}@{binding.version_designator!r}."
            )
        return matches[0]


def profile_edition_binding(
    *,
    identifier: ProfileIdentifier,
    version: VersionDesignator,
    immutable_designator: ImmutableDesignator,
) -> ExactEditionBinding:
    return ExactEditionBinding(
        kind=EditionKind.PROFILE,
        family_identifier=identifier,
        version_designator=version,
        immutable_designator=immutable_designator,
    )


def companion_edition_binding(
    *,
    identifier: CompanionIdentifier,
    version: VersionDesignator,
    immutable_designator: ImmutableDesignator,
) -> ExactEditionBinding:
    return ExactEditionBinding(
        kind=EditionKind.COMPANION,
        family_identifier=identifier,
        version_designator=version,
        immutable_designator=immutable_designator,
    )


def external_edition_binding(
    *,
    identifier: str,
    version: VersionDesignator,
    immutable_designator: ImmutableDesignator,
) -> ExactEditionBinding:
    return ExactEditionBinding(
        kind=EditionKind.EXTERNAL,
        family_identifier=identifier,
        version_designator=version,
        immutable_designator=immutable_designator,
    )


def profile_edition(
    *,
    identifier: ProfileIdentifier,
    version: VersionDesignator,
    immutable_designator: ImmutableDesignator,
    title: str,
    scope: str,
    owning_publisher: PublisherIdentifier,
) -> ExactEdition:
    return ExactEdition(
        kind=EditionKind.PROFILE,
        family_identifier=identifier,
        version_designator=version,
        immutable_designator=immutable_designator,
        title=title,
        scope=scope,
        owning_publisher=owning_publisher,
    )


def companion_edition(
    *,
    identifier: CompanionIdentifier,
    version: VersionDesignator,
    immutable_designator: ImmutableDesignator,
    title: str,
    scope: str,
    owning_publisher: PublisherIdentifier,
) -> ExactEdition:
    return ExactEdition(
        kind=EditionKind.COMPANION,
        family_identifier=identifier,
        version_designator=version,
        immutable_designator=immutable_designator,
        title=title,
        scope=scope,
        owning_publisher=owning_publisher,
    )


def external_edition(
    *,
    identifier: str,
    version: VersionDesignator,
    immutable_designator: ImmutableDesignator,
    title: str,
    scope: str,
    owning_publisher: PublisherIdentifier,
) -> ExactEdition:
    return ExactEdition(
        kind=EditionKind.EXTERNAL,
        family_identifier=identifier,
        version_designator=version,
        immutable_designator=immutable_designator,
        title=title,
        scope=scope,
        owning_publisher=owning_publisher,
    )


def resolve_exact_edition(
    *,
    catalog: EditionCatalog,
    binding: ExactEditionBinding,
) -> ExactEdition:
    return catalog.resolve(binding=binding)
