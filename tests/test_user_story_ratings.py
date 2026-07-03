"""Public user-story rating submission, including score-range and payload validation."""

from app.api.v1.community import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import (
    feature_flags as feature_repository,
    user_story_ratings as repository,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
import inspect
import pytest
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings(app_env="local")
    return TestClient(app)


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
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


def _rating_row(status: str = "pending") -> dict[str, Any]:
    return {
        "id": "66666666-6666-6666-6666-666666666666",
        "user_story_id": None,
        "country_slug": "uruguay",
        "route_id": None,
        "official_expectation_score": 80,
        "real_experience_score": 40,
        "bureaucracy_score": 60,
        "cost_surprise_score": None,
        "banking_difficulty_score": None,
        "safety_feeling_score": None,
        "comment": "Harder than expected.",
        "status": status,
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
    }


def test_repository_is_sql_only() -> None:
    source = inspect.getsource(repository)

    assert "fastapi" not in source
    assert "INSERT INTO user_story_ratings" in source


def test_public_create_user_story_rating_is_pending(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    monkeypatch.setattr(
        repository, "insert_user_story_rating", lambda *_a, **_kw: _rating_row()
    )

    response = _client().post(
        "/api/v1/community/user-story-ratings",
        json={
            "country_slug": "uruguay",
            "official_expectation_score": 80,
            "real_experience_score": 40,
            "comment": "Harder than expected.",
            "created_by_identity_type": "anonymous_session",
            "created_by_identity_id": "local-test",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_score_out_of_range_rejected() -> None:
    from app.schemas.user_story_ratings import UserStoryRatingCreate
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UserStoryRatingCreate(official_expectation_score=150)


def test_reality_gap_final_score_not_implemented() -> None:
    import app.services.user_story_ratings as service_module

    assert not hasattr(service_module, "calculate_expat_reality_gap_score")
    assert not hasattr(service_module, "compute_reality_gap")
