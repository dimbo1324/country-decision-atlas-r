from app.core.config import Settings
from app.repositories import (
    community as repository,
    feature_flags as feature_repository,
)
from app.schemas.community import (
    CommunityAnswerCreate,
    CommunityQuestionCreate,
    CommunityVoteCreate,
)
from app.services import community as service
from fastapi import HTTPException
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = MagicMock()


def _enable_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_repository,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        feature_repository,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )


def _disable_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_repository,
        "get_feature_flag",
        lambda *_a: {
            "status": "disabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(feature_repository, "list_feature_access_rules", lambda *_a: [])


def _question_row() -> dict[str, Any]:
    return {
        "id": "q1",
        "country_slug": "uruguay",
        "topic": "residence",
        "title": "How does it work?",
        "body": "Body text",
        "status": "pending",
    }


def test_submit_question_creates_pending_and_emits_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    events: dict[str, Any] = {}
    monkeypatch.setattr(
        repository, "insert_question", lambda *_a, **_kw: _question_row()
    )
    monkeypatch.setattr(
        service, "insert_domain_event", lambda *_a, **kwargs: events.update(kwargs)
    )

    row = service.submit_question(
        CONNECTION,
        Settings(app_env="local"),
        CommunityQuestionCreate(
            topic="residence",
            title="How does it work?",
            body="Body text",
            created_by_identity_type="anonymous_session",
            created_by_identity_id="session-1",
        ),
    )

    assert row["status"] == "pending"
    assert events["event_type"] == "community_question.submitted"
    assert events["notifiable"] is False


def test_submit_question_disabled_feature_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_feature(monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        service.submit_question(
            CONNECTION,
            Settings(app_env="local"),
            CommunityQuestionCreate(
                topic="residence",
                title="How does it work?",
                body="Body text",
                created_by_identity_type="anonymous_session",
                created_by_identity_id="session-1",
            ),
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "feature_disabled"


def test_submit_answer_requires_existing_question(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(repository, "get_question", lambda *_a, **_kw: None)

    with pytest.raises(HTTPException) as exc_info:
        service.submit_answer(
            CONNECTION,
            Settings(app_env="local"),
            "missing-question",
            CommunityAnswerCreate(
                body="answer body",
                created_by_identity_type="anonymous_session",
                created_by_identity_id="session-1",
            ),
        )
    assert exc_info.value.status_code == 404


def test_submit_vote_requires_published_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(repository, "get_answer", lambda *_a, **_kw: None)

    with pytest.raises(HTTPException) as exc_info:
        service.submit_vote(
            CONNECTION,
            Settings(app_env="local"),
            "missing-answer",
            CommunityVoteCreate(
                vote_type="up",
                identity_type="anonymous_session",
                identity_id="session-1",
            ),
        )
    assert exc_info.value.status_code == 404


def test_submit_vote_returns_consensus_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    answer = {
        "id": "a1",
        "source_ids": ["source-1"],
        "evidence_item_ids": [],
        "created_at": None,
    }
    monkeypatch.setattr(repository, "get_answer", lambda *_a, **_kw: answer)
    monkeypatch.setattr(repository, "insert_vote", lambda *_a, **_kw: None)
    monkeypatch.setattr(
        repository,
        "get_vote_summary",
        lambda *_a, **_kw: {
            "up_votes": 1,
            "down_votes": 0,
            "helpful_votes": 0,
            "outdated_votes": 0,
        },
    )

    summary = service.submit_vote(
        CONNECTION,
        Settings(app_env="local"),
        "a1",
        CommunityVoteCreate(
            vote_type="up", identity_type="anonymous_session", identity_id="session-1"
        ),
    )

    assert summary.answer_id == "a1"
    assert summary.source_backed is True
