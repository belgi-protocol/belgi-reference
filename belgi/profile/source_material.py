from __future__ import annotations

from dataclasses import dataclass

from .edition import ExactEditionBinding
from .edition_catalog import exact_edition_document_for_designator

__all__ = ["ProfileExactEditionSource", "built_in_exact_edition_source"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileExactEditionSource:
    binding: ExactEditionBinding
    media_type: str
    preserved_bytes: bytes


def built_in_exact_edition_source(
    *, binding: ExactEditionBinding
) -> ProfileExactEditionSource:
    document = exact_edition_document_for_designator(
        designator=binding.immutable_designator
    )
    if (
        document.kind != binding.kind.value
        or document.family_identifier != str(binding.family_identifier)
        or document.version_designator != str(binding.version_designator)
    ):
        raise ValueError(
            "exact-edition source metadata does not match the requested binding."
        )
    return ProfileExactEditionSource(
        binding=binding,
        media_type="text/markdown; charset=utf-8",
        preserved_bytes=document.source_path.read_bytes(),
    )
