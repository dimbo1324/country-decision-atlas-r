"""Demo country conservation (Episode 5): is_demo is hidden from public read surfaces but never deletes data."""

import pytest
from app.api.v1.country_drift import get_country_drift
from app.api.v1.platform_metrics import (
    get_country_platform_metric,
    list_country_platform_metrics,
)
from app.repositories import (
    cii,
    countries,
    country_drift,
    country_pairs,
    decision_engine,
    legal_signal_events,
    platform_metrics,
    search_sources,
    trust,
)
from fastapi import HTTPException
from typing import Any
from unittest.mock import MagicMock


class _FakeCursor:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self._rows = rows or []

    def fetchall(self) -> list[dict[str, Any]]:
        return self._rows

    def fetchone(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _CapturingConnection:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def execute(self, query: str, _params: Any = ()) -> _FakeCursor:
        self.queries.append(query)
        return _FakeCursor()

    @property
    def last_query(self) -> str:
        return self.queries[-1]


@pytest.fixture
def conn() -> Any:
    return _CapturingConnection()


class TestPublicCountryListing:
    def test_list_countries_excludes_demo(self, conn: Any) -> None:
        countries.list_countries(conn, "en", 20, 0)
        assert "is_demo = FALSE" in conn.last_query

    def test_count_countries_excludes_demo(self, conn: Any) -> None:
        countries.count_countries(conn)
        assert "is_demo = FALSE" in conn.last_query

    def test_active_country_slugs_exclude_demo(self, conn: Any) -> None:
        countries.list_active_country_slugs(conn)
        assert "is_demo = FALSE" in conn.last_query

    def test_get_country_excludes_demo(self, conn: Any) -> None:
        countries.get_country(conn, "russia", "en")
        assert "is_demo = FALSE" in conn.last_query


class TestDecisionEngine:
    def test_list_decision_countries_excludes_demo(self, conn: Any) -> None:
        decision_engine.list_decision_countries(conn, ["russia"], "en")
        assert "is_demo = FALSE" in conn.last_query


class TestCii:
    def test_get_country_cii_excludes_demo(self, conn: Any) -> None:
        cii.get_country_cii(conn, "russia")
        assert "is_demo = FALSE" in conn.last_query

    def test_get_cii_for_countries_excludes_demo(self, conn: Any) -> None:
        cii.get_cii_for_countries(conn, ["russia"])
        assert "is_demo = FALSE" in conn.last_query

    def test_list_matrix_countries_excludes_demo(self, conn: Any) -> None:
        cii.list_matrix_countries(conn, ["russia"], "en")
        assert "is_demo = FALSE" in conn.last_query

    def test_get_cii_metric_values_for_countries_excludes_demo(
        self, conn: Any
    ) -> None:
        cii.get_cii_metric_values_for_countries(conn, ["russia"])
        assert "is_demo = FALSE" in conn.last_query


class TestCountryPairs:
    def test_get_country_pair_compatibility_excludes_demo(
        self, conn: Any
    ) -> None:
        country_pairs.get_country_pair_compatibility(conn, "russia", "uruguay")
        assert "is_demo = FALSE" in conn.last_query

    def test_list_destination_compatibility_excludes_demo(
        self, conn: Any
    ) -> None:
        country_pairs.list_destination_compatibility(conn, "russia")
        assert "is_demo = FALSE" in conn.last_query


class TestLegalSignalTimeline:
    def test_list_timeline_events_excludes_demo(self, conn: Any) -> None:
        legal_signal_events.list_timeline_events(
            conn, None, None, None, None, None, None, None, 10, 0
        )
        assert "is_demo = FALSE" in conn.last_query

    def test_list_timeline_years_excludes_demo(self, conn: Any) -> None:
        legal_signal_events.list_timeline_years(conn)
        assert "is_demo = FALSE" in conn.last_query

    def test_country_exists_excludes_demo(self, conn: Any) -> None:
        legal_signal_events.country_exists(conn, "russia")
        assert "is_demo = FALSE" in conn.last_query


class TestSearchIndexSources:
    def test_indexable_countries_exclude_demo(self, conn: Any) -> None:
        search_sources.list_indexable_countries(conn)
        assert "is_demo = FALSE" in conn.last_query

    def test_indexable_routes_exclude_demo(self, conn: Any) -> None:
        search_sources.list_indexable_routes(conn)
        assert "is_demo = FALSE" in conn.last_query

    def test_indexable_legal_signals_exclude_demo(self, conn: Any) -> None:
        search_sources.list_indexable_legal_signals(conn)
        assert "is_demo = FALSE" in conn.last_query

    def test_indexable_country_pairs_exclude_demo(self, conn: Any) -> None:
        search_sources.list_indexable_country_pairs(conn)
        assert "is_demo = FALSE" in conn.last_query
        assert conn.last_query.count("is_demo = FALSE") == 2


class TestTrust:
    def test_get_country_trust_score_excludes_demo(self, conn: Any) -> None:
        trust.get_country_trust_score(conn, "russia")
        assert "is_demo = FALSE" in conn.last_query

    def test_list_country_trust_scores_excludes_demo(self, conn: Any) -> None:
        trust.list_country_trust_scores(conn, ["russia"])
        assert "is_demo = FALSE" in conn.last_query
        trust.list_country_trust_scores(conn, None)
        assert "is_demo = FALSE" in conn.last_query

    def test_recompute_path_still_sees_demo_countries(self, conn: Any) -> None:
        trust.list_active_countries(conn)
        assert "is_demo" not in conn.last_query
        trust.get_trust_inputs_for_country(conn, "russia")
        assert "is_demo" not in conn.last_query


class TestDriftAndPlatformMetricsRecomputeUnaffected:
    def test_drift_recompute_repositories_still_see_demo_countries(
        self, conn: Any
    ) -> None:
        country_drift.list_countries_for_drift(conn)
        assert "is_demo" not in conn.last_query

    def test_platform_metrics_recompute_repository_still_sees_demo_countries(
        self, conn: Any
    ) -> None:
        platform_metrics.list_active_countries(conn)
        assert "is_demo" not in conn.last_query


class TestPublicRouterLevelDemoChecks:
    def test_country_drift_endpoint_hides_demo_country(
        self, monkeypatch: Any
    ) -> None:
        monkeypatch.setattr(
            country_drift,
            "get_country_for_drift",
            lambda *_a: {"id": "c1", "slug": "russia", "is_demo": True},
        )
        with pytest.raises(HTTPException) as exc_info:
            get_country_drift("russia", MagicMock(), limit=12, locale=None)
        assert exc_info.value.status_code == 404

    def test_platform_metrics_list_endpoint_hides_demo_country(
        self, monkeypatch: Any
    ) -> None:
        monkeypatch.setattr(
            "app.api.v1.platform_metrics.is_feature_enabled", lambda *_: True
        )
        monkeypatch.setattr(
            "app.api.v1.platform_metrics.pm_repo.get_country_by_slug",
            lambda *_a: {"id": "c1", "slug": "russia", "is_demo": True},
        )
        with pytest.raises(HTTPException) as exc_info:
            list_country_platform_metrics(
                "russia", MagicMock(), scenario=None, locale=None
            )
        assert exc_info.value.status_code == 404

    def test_platform_metrics_detail_endpoint_hides_demo_country(
        self, monkeypatch: Any
    ) -> None:
        monkeypatch.setattr(
            "app.api.v1.platform_metrics.is_feature_enabled", lambda *_: True
        )
        monkeypatch.setattr(
            "app.api.v1.platform_metrics.pm_repo.get_country_by_slug",
            lambda *_a: {"id": "c1", "slug": "russia", "is_demo": True},
        )
        with pytest.raises(HTTPException) as exc_info:
            get_country_platform_metric(
                "russia",
                "legal_velocity_index",
                MagicMock(),
                scenario=None,
                locale=None,
            )
        assert exc_info.value.status_code == 404
