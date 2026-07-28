from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.evidence.subject_access import (
    subject_from_item,
    subject_non_empty_identifier,
    subject_non_empty_text,
    subject_values,
)

__all__ = [
    "review_system_authoritative_subject_supported",
]


def _review_identity_present(subject: Mapping[str, object]) -> bool:
    return any(
        subject_non_empty_identifier(value)
        for value in subject_values(
            subject,
            "review_identifier",
            "review_id",
            "reviewId",
            "review_thread_identifier",
            "review_thread_id",
            "reviewThreadId",
            "thread_identifier",
            "thread_id",
            "threadId",
            "comment_identifier",
            "comment_id",
            "commentId",
            "pull_request_review_id",
            "pullRequestReviewId",
        )
    )


def _review_decision_state_present(subject: Mapping[str, object]) -> bool:
    for key in (
        "approval_count",
        "approvals",
        "approver_count",
        "blocking_count",
        "blocking_reviews",
        "requested_changes",
    ):
        for value in subject_values(subject, key):
            if isinstance(value, bool):
                return True
            if isinstance(value, int):
                return True
    return any(
        subject_non_empty_text(value)
        for value in subject_values(
            subject,
            "decision",
            "review_state",
            "reviewState",
            "conclusion",
        )
    )


def review_system_authoritative_subject_supported(item: object) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    return _review_identity_present(subject) and _review_decision_state_present(subject)
