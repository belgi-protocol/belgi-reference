"""Claim-record serialization helpers."""

from __future__ import annotations

from typing import Protocol

from belgi.carrier.exceptions import ClaimRecordError
from belgi.carrier.inventory import (
    CanonicalReference,
    ImmutableDesignator,
    JsonCompatible,
    MemberInventory,
    MemberInventoryEntry,
    MemberName,
    PackageIdentifier,
)

__all__ = ["claim_record_to_json_object"]


class _StringValue(Protocol):
    @property
    def value(self) -> str: ...


class _RootDesignatorsView(Protocol):
    def to_json_object(self) -> dict[str, JsonCompatible]: ...


class _DependencyDeclarationView(Protocol):
    @property
    def dependent_reference(self) -> CanonicalReference: ...

    @property
    def dependency_reference(self) -> CanonicalReference: ...

    @property
    def dependency_kind(self) -> _StringValue: ...


class _ReferencedSourceBindingView(Protocol):
    @property
    def source_kind(self) -> _StringValue: ...

    @property
    def designator(self) -> ImmutableDesignator: ...

    @property
    def member_reference(self) -> CanonicalReference: ...


class ClaimRecordSerializationView(Protocol):
    @property
    def package_identifier(self) -> PackageIdentifier: ...

    @property
    def root_designators(self) -> _RootDesignatorsView: ...

    @property
    def member_inventory(self) -> MemberInventory: ...

    @property
    def dependency_declarations(
        self,
    ) -> tuple[_DependencyDeclarationView, ...]: ...

    @property
    def referenced_sources(self) -> tuple[_ReferencedSourceBindingView, ...]: ...

    @property
    def package_integrity_manifest_member_name(self) -> MemberName: ...

    @property
    def package_integrity_anchor_member_name(self) -> MemberName: ...

    @property
    def notes(self) -> tuple[str, ...]: ...

    @property
    def cached_verdict(self) -> int | None: ...


def _inventory_entry_to_json(
    *,
    entry: MemberInventoryEntry,
) -> dict[str, JsonCompatible]:
    representation_payload: dict[str, JsonCompatible] = {
        "mediaType": entry.representation.media_type,
    }
    if entry.representation.schema_designator is not None:
        representation_payload["schemaDesignator"] = (
            entry.representation.schema_designator.to_json_object()
        )
    payload: dict[str, JsonCompatible] = {
        "memberRole": entry.member_role.value,
        "classification": entry.classification.value,
        "representation": representation_payload,
    }
    if entry.canonical_reference is not None:
        payload["canonicalReference"] = str(entry.canonical_reference)
    if entry.projection_rule_identifier is not None:
        payload["projectionRuleIdentifier"] = entry.projection_rule_identifier
    if entry.projection_rule_designator is not None:
        payload["projectionRuleDesignator"] = (
            entry.projection_rule_designator.to_json_object()
        )
    return payload


def _dependency_declarations_to_json(
    *,
    claim_record: ClaimRecordSerializationView,
) -> dict[str, JsonCompatible]:
    dependency_declarations: dict[str, dict[str, dict[str, list[str]]]] = {}
    for dependency in claim_record.dependency_declarations:
        dependent_reference = str(dependency.dependent_reference)
        dependency_targets = dependency_declarations.setdefault(
            dependent_reference,
            {},
        )
        dependency_reference = str(dependency.dependency_reference)
        dependency_target = dependency_targets.setdefault(
            dependency_reference,
            {"dependencyKinds": []},
        )
        dependency_kinds = dependency_target["dependencyKinds"]
        if not isinstance(dependency_kinds, list):
            raise ClaimRecordError(
                "dependencyKinds bucket must remain a mutable list during "
                "JSON assembly."
            )
        dependency_kind = dependency.dependency_kind.value
        if dependency_kind not in dependency_kinds:
            dependency_kinds.append(dependency_kind)

    for dependency_targets in dependency_declarations.values():
        if not isinstance(dependency_targets, dict):
            raise ClaimRecordError(
                "dependency declarations must remain object-shaped during "
                "JSON assembly."
            )
        for dependency_target in dependency_targets.values():
            dependency_target["dependencyKinds"].sort()

    dependency_declarations_json: dict[str, JsonCompatible] = {}
    for dependent_reference, dependency_targets in dependency_declarations.items():
        dependency_targets_json: dict[str, JsonCompatible] = {}
        for dependency_reference, dependency_target in dependency_targets.items():
            dependency_kinds_json: list[JsonCompatible] = list(
                dependency_target["dependencyKinds"]
            )
            dependency_target_json: dict[str, JsonCompatible] = {
                "dependencyKinds": dependency_kinds_json,
            }
            dependency_targets_json[dependency_reference] = dependency_target_json
        dependency_declarations_json[dependent_reference] = dependency_targets_json
    return dependency_declarations_json


def claim_record_to_json_object(
    *,
    claim_record: ClaimRecordSerializationView,
) -> dict[str, JsonCompatible]:
    member_inventory: dict[str, JsonCompatible] = {}
    for entry in claim_record.member_inventory.entries:
        member_inventory[str(entry.member_name)] = _inventory_entry_to_json(entry=entry)

    referenced_sources: dict[str, JsonCompatible] = {}
    for referenced_source in claim_record.referenced_sources:
        referenced_source_json: dict[str, JsonCompatible] = {
            "sourceKind": referenced_source.source_kind.value,
            "designator": referenced_source.designator.to_json_object(),
        }
        referenced_sources[str(referenced_source.member_reference)] = (
            referenced_source_json
        )

    notes_json: list[JsonCompatible] = list(claim_record.notes)
    payload: dict[str, JsonCompatible] = {
        "kind": "claim-record",
        "packageIdentifier": str(claim_record.package_identifier),
        "packageIntegrityManifestMember": str(
            claim_record.package_integrity_manifest_member_name
        ),
        "packageIntegrityAnchorMember": str(
            claim_record.package_integrity_anchor_member_name
        ),
        "rootDesignators": claim_record.root_designators.to_json_object(),
        "memberInventory": member_inventory,
        "dependencyDeclarations": _dependency_declarations_to_json(
            claim_record=claim_record
        ),
        "referencedSources": referenced_sources,
        "notes": notes_json,
    }
    if claim_record.cached_verdict is not None:
        payload["cachedVerdict"] = claim_record.cached_verdict
    return payload
