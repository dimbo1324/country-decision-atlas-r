"""Feature-flag gating for community and Q&A endpoints."""

import pytest
from app.core.config import Settings
from app.repositories import (
    community as repository,
    feature_flags as feature_repository,
)
from app.schemas.community import CommunityQuestionCreate
from app.services import community as service
from fastapi import HTTPException
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = MagicMock()


def _question_payload() -> CommunityQuestionCreate:
    return CommunityQuestionCreate(
        topic="residence",
        title="How does it work?",
        body="Body text",
        created_by_identity_type="anonymous_session",
        created_by_identity_id="session-1",
    )


def test_community_enabled_flag_disabled_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get(_conn: object, feature_key: str) -> dict[str, object]:
        if feature_key == "community_enabled":
            return {
                "status": "disabled",
                "access_tier": "public",
                "default_enabled": True,
            }
        return {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        }

    monkeypatch.setattr(feature_repository, "get_feature_flag", fake_get)
    monkeypatch.setattr(
        feature_repository, "list_feature_access_rules", lambda *_a: []
    )

    with pytest.raises(HTTPException) as exc_info:
        service.submit_question(
            CONNECTION, Settings(app_env="local"), _question_payload()
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "feature_disabled"


def test_qna_flag_disabled_returns_403_even_if_community_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get(_conn: object, feature_key: str) -> dict[str, object]:
        if feature_key == "community_qna_enabled":
            return {
                "status": "disabled",
                "access_tier": "public",
                "default_enabled": True,
            }
        return {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        }

    monkeypatch.setattr(feature_repository, "get_feature_flag", fake_get)
    monkeypatch.setattr(
        feature_repository, "list_feature_access_rules", lambda *_a: []
    )

    with pytest.raises(HTTPException) as exc_info:
        service.submit_question(
            CONNECTION, Settings(app_env="local"), _question_payload()
        )
    assert exc_info.value.status_code == 403


def test_feature_enabled_allows_question_submission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    monkeypatch.setattr(
        repository,
        "insert_question",
        lambda *_a, **_kw: {
            "id": "q1",
            "country_slug": None,
            "topic": "residence",
            "status": "pending",
        },
    )
    monkeypatch.setattr(service, "insert_domain_event", lambda *_a, **_kw: None)

    row = service.submit_question(
        CONNECTION, Settings(app_env="local"), _question_payload()
    )
    assert row["status"] == "pending"
