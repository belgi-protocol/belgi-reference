"""Installed exact JSON-representation procedure selection."""

from __future__ import annotations

from belgi.profile.edition_catalog import exact_edition_document_for_key
from belgi.profile.source_material import built_in_exact_edition_source

from .edition import build_json_representation_companion_edition
from .selection import PackageRepresentationSelection, select_package_representation

__all__ = ["select_installed_package_representation"]


def select_installed_package_representation(
    *,
    procedure_identifier: str,
) -> PackageRepresentationSelection:
    companion_edition = build_json_representation_companion_edition(
        immutable_designator=exact_edition_document_for_key(
            key="json-representation-companion"
        ).immutable_designator
    )
    companion_binding = companion_edition.binding
    companion_source = built_in_exact_edition_source(binding=companion_binding)
    return select_package_representation(
        procedure_identifier=procedure_identifier,
        companion_binding=companion_binding,
        supported_companion_binding=companion_binding,
        companion_source_bytes=companion_source.preserved_bytes,
    )
