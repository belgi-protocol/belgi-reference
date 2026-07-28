from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class CryptoCaseObservation:
    result: str
    reason_code: str | None = None
    digest_hex: str | None = None
    decoded_hex: str | None = None

    def to_json_object(self) -> dict[str, str]:
        document = {"result": self.result}
        if self.reason_code is not None:
            document["reasonCode"] = self.reason_code
        if self.digest_hex is not None:
            document["digestHex"] = self.digest_hex
        if self.decoded_hex is not None:
            document["decodedHex"] = self.decoded_hex
        return document


def accepted(**fields: str) -> CryptoCaseObservation:
    return CryptoCaseObservation(result="accepted", **fields)


def rejected(*, reason_code: str) -> CryptoCaseObservation:
    return CryptoCaseObservation(result="rejected", reason_code=reason_code)


__all__ = [
    "CryptoCaseObservation",
    "accepted",
    "rejected",
]
