"""Installed exact package-representation procedure bindings."""

from __future__ import annotations

from belgi.carrier.inventory import Digest, ImmutableDesignator
from belgi.carrier.package.representation.binding import PackageRepresentationBinding
from belgi.profile.companions.json_representation.installed import (
    select_installed_package_representation,
)

__all__ = ["installed_package_representation_binding"]


def installed_package_representation_binding(
    *,
    procedure_identifier: str,
) -> PackageRepresentationBinding:
    selection = select_installed_package_representation(
        procedure_identifier=procedure_identifier,
    )
    return PackageRepresentationBinding(
        procedure_identifier=selection.procedure_identifier,
        defining_source=ImmutableDesignator(
            uri=selection.defining_source.uri,
            digest=Digest(
                algorithm_id=selection.defining_source.digest.algorithm_id,
                digest_value=selection.defining_source.digest.digest_value,
            ),
        ),
    )
