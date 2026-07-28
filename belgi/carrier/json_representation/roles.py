from __future__ import annotations

from enum import Enum


class TrustedJSONRole(str, Enum):
    CLAIM_RECORD = "claim-record"
    JUDGED_OBJECT = "judged-object"
    EVIDENCE_STATE = "evidence-state"
    EVALUATOR = "evaluator"
    PACKAGE_INTEGRITY_MANIFEST = "package-integrity-manifest"
    PACKAGE_INTEGRITY_ANCHOR = "package-integrity-anchor"
    REPLAY_REPORT = "replay-report"


__all__ = ["TrustedJSONRole"]
