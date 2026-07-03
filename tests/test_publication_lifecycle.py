"""Editorial publication lifecycle status transitions: allowed and forbidden moves."""

from app.services.publication import (
    PUBLICATION_STATUSES,
    allowed_transition,
    audit_action_for_transition,
    ensure_allowed_transition,
    is_publish_transition,
)
from fastapi import HTTPException
import pytest
from typing import Any, cast


def test_statuses_tuple() -> None:
    assert set(PUBLICATION_STATUSES) == {
        "draft",
        "review",
        "published",
        "archived",
        "rejected",
    }


def test_draft_to_review_allowed() -> None:
    assert allowed_transition("draft", "review") is True


def test_draft_to_rejected_allowed() -> None:
    assert allowed_transition("draft", "rejected") is True


def test_draft_to_archived_forbidden() -> None:
    assert allowed_transition("draft", "archived") is False


def test_review_to_published_allowed() -> None:
    assert allowed_transition("review", "published") is True


def test_review_to_rejected_allowed() -> None:
    assert allowed_transition("review", "rejected") is True


def test_review_to_draft_allowed() -> None:
    assert allowed_transition("review", "draft") is True


def test_published_to_archived_allowed() -> None:
    assert allowed_transition("published", "archived") is True


def test_archived_to_published_allowed() -> None:
    assert allowed_transition("archived", "published") is True


def test_rejected_to_draft_allowed() -> None:
    assert allowed_transition("rejected", "draft") is True


def test_draft_to_published_forbidden() -> None:
    assert allowed_transition("draft", "published") is False


def test_published_to_review_forbidden() -> None:
    assert allowed_transition("published", "review") is False


def test_published_to_rejected_forbidden() -> None:
    assert allowed_transition("published", "rejected") is False


def test_archived_to_review_forbidden() -> None:
    assert allowed_transition("archived", "review") is False


def test_rejected_to_published_forbidden() -> None:
    assert allowed_transition("rejected", "published") is False


def test_unknown_old_status_forbidden() -> None:
    assert allowed_transition("unknown", "draft") is False


def test_unknown_new_status_forbidden() -> None:
    assert allowed_transition("draft", "unknown") is False


def test_ensure_allowed_transition_raises_on_forbidden() -> None:
    with pytest.raises(HTTPException) as exc_info:
        ensure_allowed_transition("draft", "published")
    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "invalid_publication_transition"
    assert detail["error"]["message"] != detail["error"]["code"]


def test_ensure_allowed_transition_passes_on_allowed() -> None:
    ensure_allowed_transition("draft", "review")


def test_is_publish_transition_true() -> None:
    assert is_publish_transition("review", "published") is True


def test_is_publish_transition_true_from_archived() -> None:
    assert is_publish_transition("archived", "published") is True


def test_is_publish_transition_false_already_published() -> None:
    assert is_publish_transition("published", "archived") is False


def test_is_publish_transition_false_not_to_published() -> None:
    assert is_publish_transition("draft", "review") is False


def test_audit_action_submitted_for_review() -> None:
    assert audit_action_for_transition("draft", "review") == "submitted_for_review"


def test_audit_action_published_from_review() -> None:
    assert audit_action_for_transition("review", "published") == "published"


def test_audit_action_archived() -> None:
    assert audit_action_for_transition("published", "archived") == "archived"


def test_audit_action_rejected_from_review() -> None:
    assert audit_action_for_transition("review", "rejected") == "rejected"


def test_audit_action_rejected_from_draft() -> None:
    assert audit_action_for_transition("draft", "rejected") == "rejected"


def test_audit_action_updated_review_to_draft() -> None:
    assert audit_action_for_transition("review", "draft") == "updated"


def test_audit_action_updated_rejected_to_draft() -> None:
    assert audit_action_for_transition("rejected", "draft") == "updated"


def test_audit_action_published_from_archived() -> None:
    assert audit_action_for_transition("archived", "published") == "published"
