"""Package-level integrity manifest for replay-package members."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.exceptions import PackageIntegrityManifestError
from belgi.carrier.inventory import (
    CanonicalReference,
    JsonCompatible,
    carrier_schema_designator,
)
from belgi.carrier.json_representation import (
    CarrierSchemaGraph,
    TrustedJSONRole,
    validate_carrier_json,
)
from belgi.carrier.parse_support import (
    parse_immutable_designator_object,
    require_allowed_keys,
    require_mapping_object,
    require_non_empty_text,
)

from .binding import (
    BoundObjectKind,
    IntegrityBinding,
    canonical_json_document_bytes,
)

__all__ = [
    "PACKAGE_INTEGRITY_MANIFEST_KIND",
    "PACKAGE_INTEGRITY_MANIFEST_MEDIA_TYPE",
    "PACKAGE_INTEGRITY_MANIFEST_SCHEMA_DESIGNATOR",
    "PackageIntegrityManifest",
    "parse_package_integrity_manifest_bytes",
]


PACKAGE_INTEGRITY_MANIFEST_KIND = "package-integrity-manifest"
PACKAGE_INTEGRITY_MANIFEST_MEDIA_TYPE = (
    "application/vnd.belgi.package-integrity-manifest+json"
)
PACKAGE_INTEGRITY_MANIFEST_SCHEMA_DESIGNATOR = carrier_schema_designator(
    schema_name="PackageIntegrityManifest.schema.json"
)


def _parse_binding_record(
    *,
    member_reference_text: str,
    value: object,
) -> IntegrityBinding:
    label = f"package-integrity-manifest.bindings.{member_reference_text}"
    payload = require_mapping_object(
        value=value,
        label=label,
        error_type=PackageIntegrityManifestError,
    )
    require_allowed_keys(
        payload=payload,
        label=label,
        allowed_keys=frozenset(
            {
                "algorithmIdentifier",
                "algorithmDesignator",
                "boundObject",
                "boundValueHex",
                "canonicalizationRuleIdentifier",
                "canonicalizationRuleDesignator",
            }
        ),
        error_type=PackageIntegrityManifestError,
    )
    canonicalization_payload = payload.get("canonicalizationRuleDesignator")
    canonicalization_identifier_payload = payload.get("canonicalizationRuleIdentifier")
    canonicalization_rule_designator = None
    if canonicalization_payload is not None:
        canonicalization_rule_designator = parse_immutable_designator_object(
            value=canonicalization_payload,
            label=f"{label}.canonicalizationRuleDesignator",
            error_type=PackageIntegrityManifestError,
        )
    return IntegrityBinding(
        member_reference=CanonicalReference(member_reference_text),
        algorithm_identifier=require_non_empty_text(
            value=payload.get("algorithmIdentifier"),
            label=f"{label}.algorithmIdentifier",
            error_type=PackageIntegrityManifestError,
        ),
        algorithm_designator=parse_immutable_designator_object(
            value=payload.get("algorithmDesignator"),
            label=f"{label}.algorithmDesignator",
            error_type=PackageIntegrityManifestError,
        ),
        bound_object=BoundObjectKind(
            require_non_empty_text(
                value=payload.get("boundObject"),
                label=f"{label}.boundObject",
                error_type=PackageIntegrityManifestError,
            )
        ),
        bound_value_hex=require_non_empty_text(
            value=payload.get("boundValueHex"),
            label=f"{label}.boundValueHex",
            error_type=PackageIntegrityManifestError,
        ),
        canonicalization_rule_identifier=(
            require_non_empty_text(
                value=canonicalization_identifier_payload,
                label=f"{label}.canonicalizationRuleIdentifier",
                error_type=PackageIntegrityManifestError,
            )
            if canonicalization_identifier_payload is not None
            else None
        ),
        canonicalization_rule_designator=canonicalization_rule_designator,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageIntegrityManifest:
    """Single preserved integrity authority for one replay package."""

    bindings: tuple[IntegrityBinding, ...]

    def __post_init__(self) -> None:
        if len(self.bindings) == 0:
            raise PackageIntegrityManifestError(
                "Package-integrity manifest must preserve at least one binding."
            )
        seen: set[CanonicalReference] = set()
        for binding in self.bindings:
            if binding.member_reference in seen:
                raise PackageIntegrityManifestError(
                    f"Duplicate package-integrity binding for {binding.member_reference!s}."
                )
            seen.add(binding.member_reference)

    def binding_for_reference(
        self,
        *,
        canonical_reference: CanonicalReference,
    ) -> IntegrityBinding:
        for binding in self.bindings:
            if binding.member_reference == canonical_reference:
                return binding
        raise PackageIntegrityManifestError(
            f"Missing package-integrity binding for {canonical_reference!s}."
        )

    def to_json_object(self) -> dict[str, JsonCompatible]:
        bindings_payload: dict[str, JsonCompatible] = {}
        for binding in sorted(
            self.bindings, key=lambda item: str(item.member_reference)
        ):
            payload: dict[str, JsonCompatible] = {
                "algorithmIdentifier": binding.algorithm_identifier,
                "algorithmDesignator": binding.algorithm_designator.to_json_object(),
                "boundObject": binding.bound_object.value,
                "boundValueHex": binding.bound_value_hex,
            }
            if binding.canonicalization_rule_identifier is not None:
                payload["canonicalizationRuleIdentifier"] = (
                    binding.canonicalization_rule_identifier
                )
            if binding.canonicalization_rule_designator is not None:
                payload["canonicalizationRuleDesignator"] = (
                    binding.canonicalization_rule_designator.to_json_object()
                )
            bindings_payload[str(binding.member_reference)] = payload
        return {
            "kind": PACKAGE_INTEGRITY_MANIFEST_KIND,
            "bindings": bindings_payload,
        }

    def to_json_bytes(self) -> bytes:
        return canonical_json_document_bytes(document=self.to_json_object())


def parse_package_integrity_manifest_bytes(
    *,
    preserved_bytes: bytes,
    schema_graph: CarrierSchemaGraph | None = None,
) -> PackageIntegrityManifest:
    outcome = validate_carrier_json(
        preserved_bytes,
        trusted_role=TrustedJSONRole.PACKAGE_INTEGRITY_MANIFEST,
        schema_graph=schema_graph,
    )
    if not outcome.accepted or not isinstance(outcome.value, dict):
        raise PackageIntegrityManifestError(
            "package-integrity manifest representation rejected at "
            f"{outcome.stage}: {outcome.result_code}."
        )
    payload = outcome.value
    kind = require_non_empty_text(
        value=payload.get("kind"),
        label="package-integrity manifest.kind",
        error_type=PackageIntegrityManifestError,
    )
    if kind != PACKAGE_INTEGRITY_MANIFEST_KIND:
        raise PackageIntegrityManifestError(
            "Unexpected package-integrity manifest kind."
        )
    bindings_payload = require_mapping_object(
        value=payload.get("bindings"),
        label="package-integrity manifest.bindings",
        error_type=PackageIntegrityManifestError,
    )
    bindings: list[IntegrityBinding] = []
    for member_reference_text, binding_payload in bindings_payload.items():
        if (
            not isinstance(member_reference_text, str)
            or member_reference_text.strip() == ""
        ):
            raise PackageIntegrityManifestError(
                "package-integrity manifest binding keys must be canonical references."
            )
        bindings.append(
            _parse_binding_record(
                member_reference_text=member_reference_text,
                value=binding_payload,
            )
        )
    return PackageIntegrityManifest(bindings=tuple(bindings))
