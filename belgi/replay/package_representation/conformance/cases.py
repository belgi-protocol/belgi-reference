from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier.package.representation.binding import PackageRepresentationBinding
from belgi.replay.package_representation.directory import (
    DirectoryEntrySnapshot,
    DirectoryProjectionSnapshot,
    project_directory_snapshot,
)
from belgi.replay.package_representation.limits import check_resource_limit
from belgi.replay.package_representation.model import RepresentationResult
from belgi.replay.package_representation.paths import (
    PathOperationResult,
    map_logical_path,
    validate_logical_path,
)
from belgi.replay.package_representation.priority import select_primary_rejection
from belgi.replay.package_representation.recovery import (
    AuthenticatedMemberBinding,
    check_recovery_bindings,
)
from belgi.replay.package_representation.stage5 import (
    Stage5TraceEntry,
    evaluate_stage5_trace,
)
from belgi.replay.package_representation.zip import project_zip_bytes

from .inputs import (
    optional_int,
    optional_replay_package_corpus_bool,
    optional_replay_package_corpus_text,
    required_bool,
    required_hex_bytes,
    required_int,
    required_mapping,
    required_mapping_array,
    required_replay_package_corpus_text,
    required_text_array,
)

_DIRECTORY_PROCEDURE_IDENTIFIER = (
    "https://belgi.dev/ids/procedure/replay-package/directory-v1"
)
_ZIP_PROCEDURE_IDENTIFIER = "https://belgi.dev/ids/procedure/replay-package/zip-v1"


def require_normative_representation_bindings(
    *,
    directory_binding: PackageRepresentationBinding,
    zip_binding: PackageRepresentationBinding,
) -> None:
    if directory_binding.procedure_identifier != _DIRECTORY_PROCEDURE_IDENTIFIER:
        raise ValueError(
            "Directory corpus observations require the normative exact directory "
            "procedure identifier."
        )
    if zip_binding.procedure_identifier != _ZIP_PROCEDURE_IDENTIFIER:
        raise ValueError(
            "ZIP corpus observations require the normative exact ZIP procedure "
            "identifier."
        )
    if directory_binding.defining_source != zip_binding.defining_source:
        raise ValueError(
            "Directory and ZIP corpus observations require one exact defining source."
        )


def observe_replay_package_representation_case(
    *,
    case: Mapping[str, object],
    directory_binding: PackageRepresentationBinding,
    zip_binding: PackageRepresentationBinding,
) -> dict[str, object]:
    operation = required_replay_package_corpus_text(case, field="operation")
    candidate = required_mapping(case, field="input")
    if operation == "portable-path-validate":
        return _result_document(
            validate_logical_path(
                required_replay_package_corpus_text(
                    candidate,
                    field="logicalPath",
                )
            )
        )
    if operation == "logical-to-physical-map":
        result = map_logical_path(
            required_replay_package_corpus_text(candidate, field="logicalPath")
        )
        document = _result_document(result)
        if result.physical_path is not None:
            document["physicalPath"] = result.physical_path
        return document
    if operation == "directory-project":
        return _directory_observation(candidate, binding=directory_binding)
    if operation == "zip-project":
        result = project_zip_bytes(
            required_hex_bytes(candidate, field="archiveHex"),
            selected_binding=zip_binding,
            supported_binding=zip_binding,
        )
        return _result_document(result, include_logical_map=True)
    if operation == "resource-limit-check":
        return _result_document(
            check_resource_limit(
                resource=required_replay_package_corpus_text(
                    candidate,
                    field="resource",
                ),
                observed=required_int(candidate, field="observed"),
            )
        )
    if operation == "priority-select":
        defects = required_mapping_array(candidate, field="detectedDefects")
        return _result_document(
            select_primary_rejection(
                (
                    required_int(defect, field="stage"),
                    required_replay_package_corpus_text(
                        defect,
                        field="resultCode",
                    ),
                )
                for defect in defects
            )
        )
    if operation == "recovery-binding-check":
        return _recovery_observation(candidate)
    if operation == "stage-5-trace":
        return _stage5_trace_observation(candidate)
    raise ValueError(f"Unknown replay-package corpus operation: {operation!r}.")


def _directory_observation(
    candidate: Mapping[str, object],
    *,
    binding: PackageRepresentationBinding,
) -> dict[str, object]:
    root = required_mapping(candidate, field="root")
    entries = required_mapping_array(candidate, field="entries")
    result = project_directory_snapshot(
        DirectoryProjectionSnapshot(
            root_node_type=required_replay_package_corpus_text(
                root,
                field="nodeType",
            ),
            root_identity_stable=optional_replay_package_corpus_bool(
                root,
                field="identityStable",
            ),
            ancestors_stable=required_bool(candidate, field="ancestorsStable"),
            entries=tuple(
                DirectoryEntrySnapshot(
                    physical_path=required_replay_package_corpus_text(
                        entry,
                        field="path",
                    ),
                    node_type=required_replay_package_corpus_text(
                        entry,
                        field="nodeType",
                    ),
                    octets=(
                        required_hex_bytes(entry, field="contentHex")
                        if "contentHex" in entry
                        else None
                    ),
                    link_count=optional_int(entry, field="linkCount"),
                    identity_stable=optional_replay_package_corpus_bool(
                        entry,
                        field="identityStable",
                    ),
                    type_stable=optional_replay_package_corpus_bool(
                        entry,
                        field="typeStable",
                    ),
                    size_stable=optional_replay_package_corpus_bool(
                        entry,
                        field="sizeStable",
                    ),
                )
                for entry in entries
            ),
        ),
        selected_binding=binding,
        supported_binding=binding,
    )
    return _result_document(result, include_logical_map=True)


def _recovery_observation(candidate: Mapping[str, object]) -> dict[str, object]:
    physical_paths = required_text_array(candidate, field="physicalPaths")
    inventory = required_mapping_array(candidate, field="authenticatedInventory")
    return _result_document(
        check_recovery_bindings(
            claim_record_state=required_replay_package_corpus_text(
                candidate,
                field="claimRecordState",
            ),
            physical_paths=physical_paths,
            authenticated_inventory=(
                AuthenticatedMemberBinding(
                    logical_name=required_replay_package_corpus_text(
                        entry,
                        field="logicalName",
                    ),
                    physical_path=required_replay_package_corpus_text(
                        entry,
                        field="physicalPath",
                    ),
                    member_role=required_replay_package_corpus_text(
                        entry,
                        field="memberRole",
                    ),
                    classification=required_replay_package_corpus_text(
                        entry,
                        field="classification",
                    ),
                    trusted_json_role=optional_replay_package_corpus_text(
                        entry,
                        field="trustedJsonRole",
                    ),
                )
                for entry in inventory
            ),
        )
    )


def _stage5_trace_observation(candidate: Mapping[str, object]) -> dict[str, object]:
    entries = required_mapping_array(candidate, field="entries")
    return evaluate_stage5_trace(
        entries=tuple(
            Stage5TraceEntry(
                physical_path=required_replay_package_corpus_text(
                    entry,
                    field="physicalPath",
                ),
                method=required_replay_package_corpus_text(entry, field="method"),
                declared_uncompressed_octets=required_int(
                    entry,
                    field="declaredUncompressedOctets",
                ),
                produced_octets=required_int(entry, field="producedOctets"),
                stream_complete=required_bool(entry, field="streamComplete"),
                crc_matches=required_bool(entry, field="crcMatches"),
                compressed_boundary_exact=required_bool(
                    entry,
                    field="compressedBoundaryExact",
                ),
            )
            for entry in entries
        ),
        member_maximum=required_int(candidate, field="memberMaximum"),
        total_maximum=required_int(candidate, field="totalMaximum"),
    ).to_json_object()


def _result_document(
    result: PathOperationResult | RepresentationResult,
    *,
    include_logical_map: bool = False,
) -> dict[str, object]:
    document: dict[str, object] = {
        "accepted": result.accepted,
        "stage": result.stage,
        "resultCode": result.result_code,
    }
    logical_map = (
        result.logical_map if isinstance(result, RepresentationResult) else None
    )
    if include_logical_map and logical_map is not None:
        document["logicalMap"] = [
            {
                "logicalPath": member.logical_path,
                "octetsHex": member.octets.hex(),
            }
            for member in logical_map
        ]
    return document


__all__ = [
    "observe_replay_package_representation_case",
    "require_normative_representation_bindings",
]
