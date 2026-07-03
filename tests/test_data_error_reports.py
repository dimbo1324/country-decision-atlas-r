from app.api.v1.community import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import (
    data_error_reports as repository,
    feature_flags as feature_repository,
)
from app.services import data_error_reports as service
from fastapi import FastAPI, HTTPException
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


def _report_row(status: str = "pending") -> dict[str, Any]:
    return {
        "id": "55555555-5555-5555-5555-555555555555",
        "entity_type": "legal_signal",
        "entity_id": None,
        "country_slug": "uruguay",
        "route_id": None,
        "report_type": "outdated",
        "message": "This looks outdated.",
        "status": status,
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
        "resolution_note": None,
    }


def test_repository_is_sql_only() -> None:
    source = inspect.getsource(repository)

    assert "fastapi" not in source
    assert "INSERT INTO data_error_reports" in source


def test_repository_exposes_pending_report_counter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_count(_conn: Any, status: str | None = None) -> int:
        captured["status"] = status
        return 3

    monkeypatch.setattr(repository, "count_data_error_reports", fake_count)

    assert repository.count_pending_data_error_reports(CONNECTION) == 3
    assert captured["status"] == "pending"


def test_public_create_data_error_report_is_pending(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    monkeypatch.setattr(
        repository, "insert_data_error_report", lambda *_a, **_kw: _report_row()
    )
    monkeypatch.setattr(service, "insert_domain_event", lambda *_a, **_kw: None)

    response = _client().post(
        "/api/v1/community/data-error-reports",
        json={
            "entity_type": "legal_signal",
            "report_type": "outdated",
            "message": "This looks outdated.",
            "created_by_identity_type": "anonymous_session",
            "created_by_identity_id": "local-test",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_update_missing_report_raises_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repository, "update_data_error_report_status", lambda *_a, **_kw: None
    )

    with pytest.raises(HTTPException) as exc_info:
        service.update_data_error_report_status(
            CONNECTION, "missing", "resolved", "editor", "fixed"
        )
    assert exc_info.value.status_code == 404


def test_invalid_report_type_rejected() -> None:
    from app.schemas.data_error_reports import DataErrorReportCreate
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DataErrorReportCreate(
            entity_type="legal_signal",
            report_type="not_a_real_type",
            message="msg",
            created_by_identity_type="anonymous_session",
            created_by_identity_id="x",
        )
