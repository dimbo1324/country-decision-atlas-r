from datetime import UTC, datetime
import pytest
from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.cii"
_SVC = "app.services.country_read_model"

_CII_ROW: dict[str, Any] = {
    "overall_score": 36.42,
    "confidence": "high",
    "drift": None,
    "version": "v1.0",
    "calculated_at": datetime(2024, 1, 1, tzinfo=UTC),
    "metrics": [
        {
            "slug": "rule_of_law",
            "name_en": "Rule of Law",
            "name_ru": "Верховенство права",
            "score": 20.0,
            "weight": 0.1667,
            "weighted_score": 3.33,
            "data_year": 2023,
            "source_name": "World Bank WGI 2023",
            "reliability": "high",
        },
        {
            "slug": "economic_freedom",
            "name_en": "Economic Freedom",
            "name_ru": "Экономическая свобода",
            "score": 54.2,
            "weight": 0.1667,
            "weighted_score": 9.04,
            "data_year": 2024,
            "source_name": "Heritage Foundation",
            "reliability": "high",
        },
    ],
}


class TestBuildCii:
    def test_returns_none_for_none_row(self) -> None:
        from app.services.country_read_model import build_cii

        assert build_cii(None) is None

    def test_builds_cii_from_row(self) -> None:
        from app.services.country_read_model import build_cii

        cii = build_cii(_CII_ROW)
        assert cii is not None
        assert cii.overall_score == pytest.approx(36.42)
        assert cii.confidence == "high"
        assert cii.drift is None
        assert cii.version == "v1.0"
        assert len(cii.metrics) == 2
        assert cii.metrics[0].slug == "rule_of_law"
        assert cii.metrics[1].slug == "economic_freedom"

    def test_metrics_fields_mapped(self) -> None:
        from app.services.country_read_model import build_cii

        cii = build_cii(_CII_ROW)
        assert cii is not None
        m = cii.metrics[0]
        assert m.name_en == "Rule of Law"
        assert m.score == pytest.approx(20.0)
        assert m.weight == pytest.approx(0.1667)
        assert m.data_year == 2023

    def test_drift_is_float_when_present(self) -> None:
        from app.services.country_read_model import build_cii

        row = {**_CII_ROW, "drift": 2.5}
        cii = build_cii(row)
        assert cii is not None
        assert cii.drift == pytest.approx(2.5)

    def test_empty_metrics_list(self) -> None:
        from app.services.country_read_model import build_cii

        row = {**_CII_ROW, "metrics": []}
        cii = build_cii(row)
        assert cii is not None
        assert cii.metrics == []


class TestGetCountryCiiRepository:
    def test_calls_fetch_one_with_slug_and_version(self) -> None:
        from app.repositories.cii import get_country_cii

        conn = MagicMock()
        with patch(f"{_REPO}.fetch_one", return_value=_CII_ROW) as mock_fetch:
            result = get_country_cii(conn, "russia", "v1.0")
        assert result is _CII_ROW
        sql = mock_fetch.call_args[0][1]
        assert "country_cii_scores" in sql
        assert "country_slug" in sql or "%s" in sql

    def test_returns_none_when_not_found(self) -> None:
        from app.repositories.cii import get_country_cii

        conn = MagicMock()
        with patch(f"{_REPO}.fetch_one", return_value=None):
            result = get_country_cii(conn, "unknown-country", "v1.0")
        assert result is None


class TestCiiInReadModel:
    def _make_read_model_deps(self) -> dict[str, Any]:
        return {
            "get_country_read_model_country": {
                "id": "c1",
                "slug": "russia",
                "iso_code": "RU",
                "name": "Russia",
                "region": "Europe",
                "status": "published",
                "updated_at": datetime(2024, 1, 1, tzinfo=UTC),
                "translation_status": "source",
                "resolved_locale": "en",
            },
            "get_country_read_model_profile": None,
            "list_country_read_model_scores": [],
            "list_country_read_model_score_breakdowns": [],
            "list_country_read_model_legal_signals": [],
            "list_country_read_model_sources": [],
            "get_country_read_model_evidence_summary": {
                "total": 0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0,
            },
            "get_country_read_model_user_stories_summary": {
                "total": 0,
                "synthetic": 0,
                "average_satisfaction_score": None,
            },
        }

    def test_cii_included_in_read_model_when_present(self) -> None:
        from app.services.country_read_model import get_country_read_model

        deps = self._make_read_model_deps()
        conn = MagicMock()
        with (
            patch(
                f"{_SVC}.get_country_read_model_country",
                return_value=deps["get_country_read_model_country"],
            ),
            patch(f"{_SVC}.get_country_read_model_profile", return_value=None),
            patch(f"{_SVC}.list_country_read_model_scores", return_value=[]),
            patch(f"{_SVC}.list_country_read_model_score_breakdowns", return_value=[]),
            patch(f"{_SVC}.list_country_read_model_legal_signals", return_value=[]),
            patch(f"{_SVC}.list_country_read_model_sources", return_value=[]),
            patch(
                f"{_SVC}.get_country_read_model_evidence_summary",
                return_value=deps["get_country_read_model_evidence_summary"],
            ),
            patch(
                f"{_SVC}.get_country_read_model_user_stories_summary",
                return_value=deps["get_country_read_model_user_stories_summary"],
            ),
            patch(f"{_SVC}.get_country_cii", return_value=_CII_ROW),
            patch(
                f"{_SVC}.overlay_localized_fields",
                side_effect=lambda _conn, items, *_a, **_kw: items,
            ),
        ):
            result = get_country_read_model(conn, "russia", "en")
        assert result is not None
        assert result.cii is not None
        assert result.cii.overall_score == pytest.approx(36.42)
        assert result.cii.version == "v1.0"

    def test_cii_is_none_in_read_model_when_absent(self) -> None:
        from app.services.country_read_model import get_country_read_model

        deps = self._make_read_model_deps()
        conn = MagicMock()
        with (
            patch(
                f"{_SVC}.get_country_read_model_country",
                return_value=deps["get_country_read_model_country"],
            ),
            patch(f"{_SVC}.get_country_read_model_profile", return_value=None),
            patch(f"{_SVC}.list_country_read_model_scores", return_value=[]),
            patch(f"{_SVC}.list_country_read_model_score_breakdowns", return_value=[]),
            patch(f"{_SVC}.list_country_read_model_legal_signals", return_value=[]),
            patch(f"{_SVC}.list_country_read_model_sources", return_value=[]),
            patch(
                f"{_SVC}.get_country_read_model_evidence_summary",
                return_value=deps["get_country_read_model_evidence_summary"],
            ),
            patch(
                f"{_SVC}.get_country_read_model_user_stories_summary",
                return_value=deps["get_country_read_model_user_stories_summary"],
            ),
            patch(f"{_SVC}.get_country_cii", return_value=None),
            patch(
                f"{_SVC}.overlay_localized_fields",
                side_effect=lambda _conn, items, *_a, **_kw: items,
            ),
        ):
            result = get_country_read_model(conn, "russia", "en")
        assert result is not None
        assert result.cii is None


class TestCiiSchemas:
    def test_country_read_model_cii_validates(self) -> None:
        from app.schemas.country_read_model import CountryReadModelCii

        cii = CountryReadModelCii.model_validate(
            {
                "overall_score": 36.42,
                "confidence": "high",
                "drift": None,
                "version": "v1.0",
                "calculated_at": "2024-01-01T00:00:00Z",
                "metrics": [],
            }
        )
        assert cii.overall_score == pytest.approx(36.42)
        assert cii.metrics == []

    def test_country_read_model_cii_metric_validates(self) -> None:
        from app.schemas.country_read_model import CountryReadModelCiiMetric

        m = CountryReadModelCiiMetric.model_validate(
            {
                "slug": "rule_of_law",
                "name_en": "Rule of Law",
                "name_ru": "Верховенство права",
                "score": 20.0,
                "weight": 0.1667,
                "weighted_score": 3.33,
            }
        )
        assert m.slug == "rule_of_law"
        assert m.data_year is None
        assert m.reliability is None
