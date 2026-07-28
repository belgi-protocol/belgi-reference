"""Carrier inventory immutable designators."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

from belgi.carrier.exceptions import (
    InvalidDigestError,
    InvalidRepresentationBindingError,
    MemberError,
)

from .payload import JsonCompatible

SCHEMA_ID_BASE = "https://belgi.dev/schemas/carrier/rc.v2"
_SCHEMA_DIGESTS: dict[str, str] = {
    "BELGI-JSON-Schema-Dialect.schema.json": "ae5950ff6aca362afa1872950b3989c7e83b17df9f497bcd70a60c1527b6e8fc",
    "ClaimRecord.schema.json": "b679bb09bba56f334f65d2ecb2cc747ea4b3fcef5a7c8bf155585187b26e57d2",
    "Common.schema.json": "92f709ea955937e546ece8a2be4ef1183586710e557c98b5cfcb0c729a83debd",
    "EvaluatorCarrier.schema.json": "93e289161857a594028d66d93599c0e34a7dbde65d986738676de7b3dc14c0cd",
    "EvidenceStateCarrier.schema.json": "e5b9b131bca0ae96447cd3a063d62ca90f83852cb10a0937dd8a79248f618d58",
    "FailureTaxonomy.schema.json": "a0683d60d24b3f5f60d7e776c50c9ee66456fafb8e64e54ceb79d63491bfaf3a",
    "JudgedObjectCarrier.schema.json": "f6c407ece43fa68938e33da4b495a244aadd4ff6bedb9774601c952edceef201",
    "OperationalActionJudgedObjectCarrier.schema.json": "12965b17120d88ade785f82a454ce1ea84ee9ff96a33f763796caef69ceb5ee8",
    "PackageIntegrityAnchor.schema.json": "5a5756e043bab35b1c763ece90f53f695cf954a5b7e56eff4489a5e9b8f1ace7",
    "PackageIntegrityManifest.schema.json": "51f0541351d25c4eb90a5a31e05e23d19c19f1aab32a0b346d54ec8451f553a0",
    "ReplayReport.schema.json": "989f25369d38250b862540ae84e5bfeb71464ca2fe4ed9b48a716bfef1cafade",
}

__all__ = [
    "SCHEMA_ID_BASE",
    "Digest",
    "ImmutableDesignator",
    "carrier_schema_designator",
    "carrier_schema_digests",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class Digest:
    """Digest component of one immutable designator."""

    algorithm_id: str
    digest_value: str

    def __post_init__(self) -> None:
        if self.algorithm_id.strip() == "":
            raise InvalidDigestError("algorithm_id must be non-empty.")
        if self.digest_value.strip() == "":
            raise InvalidDigestError("digest_value must be non-empty.")
        if len(self.digest_value) % 2 != 0:
            raise InvalidDigestError("digest_value must contain full octets.")
        if any(character not in "0123456789abcdef" for character in self.digest_value):
            raise InvalidDigestError("digest_value must be lowercase hexadecimal.")

    def to_json_object(self) -> dict[str, JsonCompatible]:
        return {
            "algorithmId": self.algorithm_id,
            "digestValue": self.digest_value,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ImmutableDesignator:
    """Structured immutable designator for exact edition binding."""

    uri: str
    digest: Digest

    def __post_init__(self) -> None:
        parsed = urlparse(self.uri)
        if not parsed.scheme:
            raise InvalidRepresentationBindingError("uri must be an absolute URI.")
        if parsed.scheme in {"http", "https"} and not parsed.netloc:
            raise InvalidRepresentationBindingError(
                "uri must include an authority when using HTTP(S)."
            )

    def to_json_object(self) -> dict[str, JsonCompatible]:
        return {
            "uri": self.uri,
            "digest": self.digest.to_json_object(),
        }

    def __str__(self) -> str:
        return f"{self.uri}#{self.digest.algorithm_id}:{self.digest.digest_value}"


def carrier_schema_designator(*, schema_name: str) -> ImmutableDesignator:
    digest_value = _SCHEMA_DIGESTS.get(schema_name)
    if digest_value is None:
        raise MemberError(f"Unknown carrier schema name: {schema_name}")
    return ImmutableDesignator(
        uri=f"{SCHEMA_ID_BASE}/{schema_name}",
        digest=Digest(
            algorithm_id="sha256",
            digest_value=digest_value,
        ),
    )


def carrier_schema_digests() -> dict[str, str]:
    return dict(_SCHEMA_DIGESTS)


def replace_carrier_schema_digests(*, schema_digests: Mapping[str, str]) -> None:
    _SCHEMA_DIGESTS.clear()
    _SCHEMA_DIGESTS.update(schema_digests)
