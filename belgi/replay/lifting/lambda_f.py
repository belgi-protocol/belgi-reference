from __future__ import annotations

from belgi.carrier import ClaimRecord, MemberInventoryEntry
from belgi.replay.context import (
    EvaluatorParsedT,
    EvaluatorResolvedT,
    EvaluatorT,
    EvidenceParsedT,
    EvidenceResolvedT,
    EvidenceT,
    JudgedParsedT,
    JudgedResolvedT,
    JudgedT,
    ReplayContext,
    VerdictT,
)
from belgi.replay.package_source.protocol import ReplayPackageSource

from .dependencies import resolve_declared_dependencies
from .exceptions import (
    INDUCE_STAGE,
    PARSE_STAGE,
    RESOLVE_STAGE,
    InduceFailureError,
    ParseFailureError,
    ResolveFailureError,
)
from .members import read_member_bytes
from .model import (
    InduceRecord,
    LiftingTrace,
    ParseRecord,
    ResolveRecord,
)


def lift_evaluator(
    *,
    package: ReplayPackageSource,
    claim_record: ClaimRecord,
    root_member: MemberInventoryEntry,
    replay_context: ReplayContext[
        JudgedParsedT,
        JudgedResolvedT,
        EvidenceParsedT,
        EvidenceResolvedT,
        EvaluatorParsedT,
        EvaluatorResolvedT,
        JudgedT,
        EvidenceT,
        EvaluatorT,
        VerdictT,
    ],
) -> LiftingTrace[EvaluatorParsedT, EvaluatorResolvedT, EvaluatorT]:
    root_reference = root_member.canonical_reference
    if root_reference is None:
        raise ParseFailureError(
            message="Evaluator root member lacks a canonical reference."
        )
    try:
        root_bytes = read_member_bytes(package=package, member=root_member)
    except Exception as exc:
        raise ParseFailureError(
            message=f"Could not read evaluator root member {root_member.member_name!r}.",
            related_reference=root_reference,
        ) from exc

    try:
        parsed = replay_context.evaluator_lifting.parse(
            root_member=root_member,
            root_bytes=root_bytes,
            claim_record=claim_record,
        )
    except ParseFailureError:
        raise
    except Exception as exc:
        raise ParseFailureError(
            message=f"Evaluator carrier parse failed: {exc}",
            related_reference=root_reference,
        ) from exc

    dependencies = resolve_declared_dependencies(
        claim_record=claim_record,
        package=package,
        source_member=root_member,
        dependency_references=parsed.dependency_references,
        exact_edition_designators=parsed.exact_edition_designators,
    )

    try:
        resolved = replay_context.evaluator_lifting.resolve(
            parsed=parsed,
            dependencies=dependencies,
            claim_record=claim_record,
        )
    except ResolveFailureError:
        raise
    except Exception as exc:
        raise ResolveFailureError(
            message=f"Evaluator carrier resolution failed: {exc}",
            related_reference=root_reference,
        ) from exc

    try:
        induced = replay_context.evaluator_lifting.induce(
            resolved=resolved,
            claim_record=claim_record,
        )
    except InduceFailureError:
        raise
    except Exception as exc:
        raise InduceFailureError(
            message=f"Evaluator induction failed: {exc}",
            related_reference=root_reference,
        ) from exc
    return LiftingTrace(
        parsed=ParseRecord(
            stage=PARSE_STAGE,
            root_reference=root_reference,
            value=parsed.parsed_carrier,
        ),
        resolved=ResolveRecord(
            stage=RESOLVE_STAGE,
            root_reference=root_reference,
            value=resolved.resolved_carrier,
        ),
        induced=InduceRecord(
            stage=INDUCE_STAGE,
            root_reference=root_reference,
            value=induced.semantic_object,
        ),
    )


__all__ = ["lift_evaluator"]
