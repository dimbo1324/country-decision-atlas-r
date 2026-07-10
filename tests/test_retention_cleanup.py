"""Retention cleanup (P1-4, Аудит-эпизод 5): dry-run counts vs real deletes,
cutoff dates derived from methodology_config.py, and that pending/in_flight
domain_events are never touched."""

from app.repositories import retention as repository
from app.services import retention as retention_service
from app.services.methodology_config import (
    AuthorMetricsThresholds,
    BoardLimits,
    ConfidenceThresholds,
    DecisionThresholds,
    MethodologyConfig,
    RecommendationThresholds,
    RetentionThresholds,
    ScoreLabelThresholds,
    TripWarningThresholds,
)
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from unittest.mock import MagicMock


def _config(**retention_overrides: int) -> MethodologyConfig:
    defaults: dict[str, int] = {
        "analytics_days": 180,
        "domain_events_days": 30,
        "sessions_days": 30,
    }
    defaults.update(retention_overrides)
    return MethodologyConfig(
        version="v1.0",
        parameters={},
        score_labels=ScoreLabelThresholds(30.0, 50.0, 70.0, 85.0),
        decision=DecisionThresholds(
            strength_min_score=70.0,
            weakness_max_score=50.0,
            confidence=ConfidenceThresholds(2.5, 1.7),
            recommendation=RecommendationThresholds(3.0, 10.0),
        ),
        board=BoardLimits(5, 20, 20, 3, 50),
        flows_k_anonymity=20,
        trip_warnings=TripWarningThresholds(3, 3, 2),
        author_metrics=AuthorMetricsThresholds(120, 5),
        retention=RetentionThresholds(**defaults),
    )


def test_dry_run_calls_count_functions_and_never_deletes(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        retention_service,
        "get_active_methodology_config",
        lambda _conn: _config(),
    )
    counters = {
        "count_expired_analytics_events": MagicMock(return_value=3),
        "count_expired_ai_interaction_logs": MagicMock(return_value=4),
        "count_relayed_domain_events": MagicMock(return_value=5),
        "count_expired_auth_sessions": MagicMock(return_value=6),
    }
    deleters = {
        "delete_expired_analytics_events": MagicMock(),
        "delete_expired_ai_interaction_logs": MagicMock(),
        "delete_relayed_domain_events": MagicMock(),
        "delete_expired_auth_sessions": MagicMock(),
    }
    for name, mock in {**counters, **deleters}.items():
        monkeypatch.setattr(repository, name, mock)

    connection = cast(Any, MagicMock())
    result = retention_service.run_retention_cleanup(connection, dry_run=True)

    for mock in deleters.values():
        mock.assert_not_called()
    for mock in counters.values():
        mock.assert_called_once()

    assert result["dry_run"] is True
    assert result["summary"] == {
        "analytics_events_deleted": 3,
        "ai_interaction_logs_deleted": 4,
        "domain_events_deleted": 5,
        "auth_sessions_deleted": 6,
    }


def test_real_run_calls_delete_functions_and_never_counts(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        retention_service,
        "get_active_methodology_config",
        lambda _conn: _config(),
    )
    counters = {
        "count_expired_analytics_events": MagicMock(),
        "count_expired_ai_interaction_logs": MagicMock(),
        "count_relayed_domain_events": MagicMock(),
        "count_expired_auth_sessions": MagicMock(),
    }
    deleters = {
        "delete_expired_analytics_events": MagicMock(return_value=1),
        "delete_expired_ai_interaction_logs": MagicMock(return_value=2),
        "delete_relayed_domain_events": MagicMock(return_value=0),
        "delete_expired_auth_sessions": MagicMock(return_value=7),
    }
    for name, mock in {**counters, **deleters}.items():
        monkeypatch.setattr(repository, name, mock)

    connection = cast(Any, MagicMock())
    result = retention_service.run_retention_cleanup(connection, dry_run=False)

    for mock in counters.values():
        mock.assert_not_called()
    for mock in deleters.values():
        mock.assert_called_once()

    assert result["dry_run"] is False
    assert result["summary"]["auth_sessions_deleted"] == 7


def test_cutoffs_are_derived_from_methodology_config_days(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        retention_service,
        "get_active_methodology_config",
        lambda _conn: _config(
            analytics_days=10, domain_events_days=2, sessions_days=5
        ),
    )
    captured: dict[str, Any] = {}

    def capture_analytics(_conn: Any, cutoff: datetime) -> int:
        captured["analytics"] = cutoff
        return 0

    def capture_domain_events(_conn: Any, cutoff: datetime) -> int:
        captured["domain_events"] = cutoff
        return 0

    def capture_sessions(_conn: Any, cutoff: datetime) -> int:
        captured["sessions"] = cutoff
        return 0

    monkeypatch.setattr(
        repository, "count_expired_analytics_events", capture_analytics
    )
    monkeypatch.setattr(
        repository,
        "count_expired_ai_interaction_logs",
        lambda _conn, _cutoff: 0,
    )
    monkeypatch.setattr(
        repository, "count_relayed_domain_events", capture_domain_events
    )
    monkeypatch.setattr(
        repository, "count_expired_auth_sessions", capture_sessions
    )

    before = datetime.now(UTC)
    retention_service.run_retention_cleanup(
        cast(Any, MagicMock()), dry_run=True
    )
    after = datetime.now(UTC)

    assert (
        before - timedelta(days=10, seconds=1)
        <= captured["analytics"]
        <= after - timedelta(days=10)
    )
    assert (
        before - timedelta(days=2, seconds=1)
        <= captured["domain_events"]
        <= after - timedelta(days=2)
    )
    assert (
        before - timedelta(days=5, seconds=1)
        <= captured["sessions"]
        <= after - timedelta(days=5)
    )


def test_delete_relayed_domain_events_sql_filters_by_status_relayed() -> None:
    # Guards the P1-1/P1-4 invariant: retention must only ever target
    # status='relayed' rows. If someone edits the SQL to drop that filter,
    # this test fails loudly instead of silently letting pending/in_flight
    # outbox events get swept.
    import inspect

    source = inspect.getsource(repository.delete_relayed_domain_events)
    assert "status = 'relayed'" in source
