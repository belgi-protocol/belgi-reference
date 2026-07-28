"""Carrier inventory representation bindings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from belgi.carrier.exceptions import (
    InvalidContentLocatorError,
    InvalidMemberNameError,
    InvalidRepresentationBindingError,
)

from .designators import ImmutableDesignator
from .identity import MemberName, ParameterIdentifier, ReferenceResolver
from .payload import JsonCompatible, JsonPayload

__all__ = [
    "ContentLocator",
    "ContentLocatorMode",
    "DeclarationParameter",
    "RepresentationBinding",
]


def _inventory_representation_required_text(*, value: str, label: str) -> None:
    if value.strip() == "":
        raise InvalidMemberNameError(f"{label} must be non-empty.")


class ContentLocatorMode(str, Enum):
    """How replay-relevant content is preserved inside a carrier document."""

    INLINE_JSON = "inline-json"
    PACKAGE_MEMBER = "package-member"


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentLocator:
    """Replay-relevant content designated inline or through a package member."""

    mode: ContentLocatorMode
    media_type: str
    inline_json: JsonPayload | None = None
    member_name: MemberName | None = None

    def __post_init__(self) -> None:
        _inventory_representation_required_text(
            value=self.media_type,
            label="media_type",
        )
        if self.mode is ContentLocatorMode.INLINE_JSON:
            if self.inline_json is None or self.member_name is not None:
                raise InvalidContentLocatorError(
                    "Inline JSON content locators require inline_json and forbid "
                    "member_name."
                )
            return
        if self.mode is ContentLocatorMode.PACKAGE_MEMBER:
            if self.member_name is None or self.inline_json is not None:
                raise InvalidContentLocatorError(
                    "Package-member content locators require member_name and "
                    "forbid inline_json."
                )
            _inventory_representation_required_text(
                value=str(self.member_name),
                label="member_name",
            )
            return
        raise InvalidContentLocatorError(
            f"Unsupported content locator mode: {self.mode!r}"
        )

    @classmethod
    def inline_json_locator(
        cls,
        *,
        media_type: str,
        content: JsonPayload,
    ) -> ContentLocator:
        return cls(
            mode=ContentLocatorMode.INLINE_JSON,
            media_type=media_type,
            inline_json=content,
        )

    @classmethod
    def inline_value(
        cls,
        *,
        media_type: str,
        value: JsonCompatible,
    ) -> ContentLocator:
        return cls.inline_json_locator(
            media_type=media_type,
            content=JsonPayload.from_value(value=value),
        )

    @classmethod
    def package_member(
        cls,
        *,
        media_type: str,
        member_name: MemberName,
    ) -> ContentLocator:
        return cls(
            mode=ContentLocatorMode.PACKAGE_MEMBER,
            media_type=media_type,
            member_name=member_name,
        )

    def referenced_member_names(self) -> tuple[MemberName, ...]:
        if self.member_name is None:
            return ()
        return (self.member_name,)

    def to_json_object(
        self,
        *,
        resolve_reference: ReferenceResolver,
    ) -> dict[str, JsonCompatible]:
        if self.mode is ContentLocatorMode.INLINE_JSON:
            inline_json = self.inline_json
            if inline_json is None:
                raise InvalidContentLocatorError(
                    "Inline JSON content locators require inline_json."
                )
            return {
                "kind": self.mode.value,
                "mediaType": self.media_type,
                "content": inline_json.to_compatible_value(),
            }
        member_name = self.member_name
        if member_name is None:
            raise InvalidContentLocatorError(
                "Package-member content locators require member_name."
            )
        return {
            "kind": self.mode.value,
            "mediaType": self.media_type,
            "memberReference": str(resolve_reference(member_name)),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class DeclarationParameter:
    """One preserved declaration parameter."""

    parameter_identifier: ParameterIdentifier
    value: JsonPayload

    def __post_init__(self) -> None:
        _inventory_representation_required_text(
            value=str(self.parameter_identifier),
            label="parameter_identifier",
        )

    @classmethod
    def from_value(
        cls,
        *,
        parameter_identifier: ParameterIdentifier,
        value: JsonCompatible,
    ) -> DeclarationParameter:
        return cls(
            parameter_identifier=parameter_identifier,
            value=JsonPayload.from_value(value=value),
        )

    def to_json_object(self) -> dict[str, JsonCompatible]:
        return {
            "parameterIdentifier": str(self.parameter_identifier),
            "value": self.value.to_compatible_value(),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RepresentationBinding:
    """Representation binding preserved for one package member."""

    media_type: str
    schema_designator: ImmutableDesignator | None = None

    def __post_init__(self) -> None:
        if self.media_type.strip() == "":
            raise InvalidRepresentationBindingError("media_type must be non-empty.")
