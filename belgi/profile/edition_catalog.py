from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from belgi.substrate.hash import sha256_file
from belgi.substrate.io import load_json_object

from .edition import Digest, ImmutableDesignator

__all__ = [
    "ExactEditionDocument",
    "exact_edition_document_for_designator",
    "exact_edition_document_for_key",
    "exact_edition_documents",
]


_CATALOG_PATH = Path(__file__).with_name("edition_catalog.json")
_PROFILE_PACKAGE_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True, slots=True, kw_only=True)
class ExactEditionDocument:
    key: str
    artifact_class: str
    publication_track: str
    kind: str
    family_identifier: str
    version_designator: str
    uri: str
    sha256: str
    snapshot_path: str

    @property
    def source_path(self) -> Path:
        return _PROFILE_PACKAGE_ROOT / self.snapshot_path

    @property
    def immutable_designator(self) -> ImmutableDesignator:
        return ImmutableDesignator(
            uri=self.uri,
            digest=Digest(algorithm_id="sha256", digest_value=self.sha256),
        )


def _edition_catalog_required_text(*, payload: dict[str, object], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"edition catalog {field} must be a non-empty string.")
    return value


def _load_exact_edition_documents() -> tuple[ExactEditionDocument, ...]:
    document = load_json_object(_CATALOG_PATH, label=str(_CATALOG_PATH))
    if document.get("schemaVersion") != "belgi-exact-edition-catalog-v1":
        raise ValueError("unsupported exact-edition catalog schemaVersion.")
    raw_entries = document.get("entries")
    if not isinstance(raw_entries, list):
        raise ValueError("exact-edition catalog entries must be an array.")
    entries: list[ExactEditionDocument] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("exact-edition catalog entry must be an object.")
        entry = ExactEditionDocument(
            key=_edition_catalog_required_text(payload=raw_entry, field="key"),
            artifact_class=_edition_catalog_required_text(
                payload=raw_entry, field="artifactClass"
            ),
            publication_track=_edition_catalog_required_text(
                payload=raw_entry, field="publicationTrack"
            ),
            kind=_edition_catalog_required_text(payload=raw_entry, field="kind"),
            family_identifier=_edition_catalog_required_text(
                payload=raw_entry, field="familyIdentifier"
            ),
            version_designator=_edition_catalog_required_text(
                payload=raw_entry, field="versionDesignator"
            ),
            uri=_edition_catalog_required_text(payload=raw_entry, field="uri"),
            sha256=_edition_catalog_required_text(payload=raw_entry, field="sha256"),
            snapshot_path=_edition_catalog_required_text(
                payload=raw_entry, field="snapshotPath"
            ),
        )
        if not entry.source_path.is_file():
            raise ValueError(
                f"exact-edition snapshot is missing: {entry.snapshot_path}."
            )
        observed_sha256 = sha256_file(entry.source_path)
        if observed_sha256 != entry.sha256:
            raise ValueError(
                f"exact-edition snapshot digest mismatch for {entry.key}: "
                f"expected {entry.sha256}, observed {observed_sha256}."
            )
        entries.append(entry)
    if len({entry.key for entry in entries}) != len(entries):
        raise ValueError("exact-edition catalog keys must be unique.")
    if len({entry.uri for entry in entries}) != len(entries):
        raise ValueError("exact-edition catalog URIs must be unique.")
    return tuple(entries)


_EXACT_EDITION_DOCUMENTS = _load_exact_edition_documents()


def exact_edition_documents() -> tuple[ExactEditionDocument, ...]:
    return _EXACT_EDITION_DOCUMENTS


def exact_edition_document_for_key(*, key: str) -> ExactEditionDocument:
    for document in _EXACT_EDITION_DOCUMENTS:
        if document.key == key:
            return document
    raise KeyError(key)


def exact_edition_document_for_designator(
    *, designator: object
) -> ExactEditionDocument:
    uri = getattr(designator, "uri", None)
    digest = getattr(designator, "digest", None)
    algorithm_id = getattr(digest, "algorithm_id", None)
    digest_value = getattr(digest, "digest_value", None)
    for document in _EXACT_EDITION_DOCUMENTS:
        if (
            document.uri == uri
            and algorithm_id == "sha256"
            and document.sha256 == digest_value
        ):
            return document
    raise KeyError((uri, algorithm_id, digest_value))
