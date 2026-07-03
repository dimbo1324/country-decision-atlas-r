from app.core.config import Settings
from app.repositories import (
    community as repository,
    data_error_reports as error_report_repository,
    feature_flags as feature_repository,
)
from app.schemas.community import CommunityAnswerCreate, CommunityQuestionCreate
from app.schemas.data_error_reports import DataErrorReportCreate
from app.services import (
    community as service,
    data_error_reports as error_report_service,
)
import pytest
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()


def _enable_all(monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_community_question_submitted_event_is_notifiable_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_all(monkeypatch)
    monkeypatch.setattr(
        repository,
        "insert_question",
        lambda *_a, **_kw: {
            "id": "q1",
            "country_slug": "uruguay",
            "topic": "t",
            "status": "pending",
        },
    )
    events: dict[str, Any] = {}
    monkeypatch.setattr(
        service, "insert_domain_event", lambda *_a, **kwargs: events.update(kwargs)
    )

    service.submit_question(
        CONNECTION,
        Settings(app_env="local"),
        CommunityQuestionCreate(
            topic="t",
            title="title",
            body="body",
            created_by_identity_type="anonymous_session",
            created_by_identity_id="s1",
        ),
    )

    assert events["event_type"] == "community_question.submitted"
    assert events["notifiable"] is False
    assert events["event_key"] == "qna_question:q1:community_question.submitted"


def test_community_answer_submitted_event_is_notifiable_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_all(monkeypatch)
    monkeypatch.setattr(
        repository,
        "get_question",
        lambda *_a, **_kw: {
            "id": "q1",
            "country_slug": "uruguay",
            "status": "published",
        },
    )
    monkeypatch.setattr(
        repository,
        "insert_answer",
        lambda *_a, **_kw: {"id": "a1", "question_id": "q1", "status": "pending"},
    )
    events: dict[str, Any] = {}
    monkeypatch.setattr(
        service, "insert_domain_event", lambda *_a, **kwargs: events.update(kwargs)
    )

    service.submit_answer(
        CONNECTION,
        Settings(app_env="local"),
        "q1",
        CommunityAnswerCreate(
            body="answer",
            created_by_identity_type="anonymous_session",
            created_by_identity_id="s1",
        ),
    )

    assert events["event_type"] == "community_answer.submitted"
    assert events["notifiable"] is False


def test_data_error_report_submitted_event_is_notifiable_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_all(monkeypatch)
    monkeypatch.setattr(
        error_report_repository,
        "insert_data_error_report",
        lambda *_a, **_kw: {
            "id": "r1",
            "country_slug": "uruguay",
            "report_type": "outdated",
            "status": "pending",
        },
    )
    events: dict[str, Any] = {}
    monkeypatch.setattr(
        error_report_service,
        "insert_domain_event",
        lambda *_a, **kwargs: events.update(kwargs),
    )

    error_report_service.submit_data_error_report(
        CONNECTION,
        Settings(app_env="local"),
        DataErrorReportCreate(
            entity_type="legal_signal",
            report_type="outdated",
            message="msg",
            created_by_identity_type="anonymous_session",
            created_by_identity_id="s1",
        ),
    )

    assert events["event_type"] == "data_error_report.submitted"
    assert events["notifiable"] is False
