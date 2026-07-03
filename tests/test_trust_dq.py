"""Data-quality checks for trust scores: invalid values and stale/inconsistent confidence states."""

from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_clean_trust_surface_produces_no_critical_issues(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is True
    trust_codes = {
        i.code
        for i in report.issues
        if "trust" in i.code or "methodology" in i.code or "glossary" in i.code
    }
    assert trust_codes == set()


def test_invalid_trust_score_value_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_trust_score_values",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "russia",
                "trust_score": 150.0,
                "trust_label": "invalid",
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "trust_score_value_invalid" for i in report.issues)
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "trust_score_value_invalid"
    )


def test_inconsistent_insufficient_data_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_inconsistent_trust_insufficient_data",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "portugal",
                "trust_score": 75.0,
                "trust_label": "insufficient_data",
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(
        i.code == "trust_score_insufficient_data_inconsistent" for i in report.issues
    )


def test_stale_trust_score_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_stale_trust_scores",
        lambda *_: [{"id": "abc123", "country_slug": "uruguay", "days_old": 45}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "trust_score_stale" for i in report.issues)
    stale_issues = [i for i in report.issues if i.code == "trust_score_stale"]
    assert all(i.severity == "warning" for i in stale_issues)
    assert report.valid is True


def test_missing_methodology_section_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_missing_required_methodology_sections",
        lambda *_: [{"slug": "what_is_trust_score"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "methodology_section_missing" for i in report.issues)
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "methodology_section_missing"
    )


def test_missing_trust_score_for_active_country_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_countries_missing_trust_scores",
        lambda *_: [{"slug": "test-country"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(
        i.code == "trust_score_missing_for_active_country" for i in report.issues
    )
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "trust_score_missing_for_active_country"
    )
    assert report.valid is False


def test_missing_glossary_term_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_missing_required_glossary_terms",
        lambda *_: [{"slug": "trust_score"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "glossary_term_missing" for i in report.issues)
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "glossary_term_missing"
    )


def test_required_methodology_slugs_covers_all_12() -> None:
    from app.repositories.data_quality.trust import REQUIRED_METHODOLOGY_SLUGS

    expected = {
        "what_is_cii",
        "what_is_decision_score",
        "what_is_persona",
        "what_is_route",
        "what_is_legal_velocity",
        "what_is_scenario_risk",
        "what_is_contradiction_score",
        "what_is_trust_score",
        "what_is_confidence",
        "what_is_freshness",
        "source_backed_methodology",
        "legal_disclaimer",
    }
    assert set(REQUIRED_METHODOLOGY_SLUGS) == expected
    assert len(REQUIRED_METHODOLOGY_SLUGS) == 12


def test_required_glossary_slugs_covers_all_19() -> None:
    from app.repositories.data_quality.trust import REQUIRED_GLOSSARY_SLUGS

    expected = {
        "residence",
        "permanent_residence",
        "citizenship",
        "legal_signal",
        "evidence",
        "source",
        "source_backed",
        "confidence",
        "freshness",
        "contradiction",
        "trust_score",
        "cii",
        "scenario",
        "persona",
        "route",
        "platform_metric",
        "legal_velocity_index",
        "scenario_specific_risk_score",
        "decision_score",
    }
    assert set(REQUIRED_GLOSSARY_SLUGS) == expected
    assert len(REQUIRED_GLOSSARY_SLUGS) == 19


def test_each_required_methodology_slug_triggers_critical(monkeypatch: Any) -> None:
    from app.repositories.data_quality.trust import REQUIRED_METHODOLOGY_SLUGS

    for slug in REQUIRED_METHODOLOGY_SLUGS:
        install_clean_report_fakes(monkeypatch)
        monkeypatch.setattr(
            data_quality_repository,
            "list_missing_required_methodology_sections",
            lambda *_, s=slug: [{"slug": s}],
        )
        report = data_quality.build_data_quality_report(CONNECTION)
        assert any(i.code == "methodology_section_missing" for i in report.issues), (
            f"no issue for {slug}"
        )
        assert report.valid is False, f"expected valid=False for missing slug {slug}"


def test_each_required_glossary_slug_triggers_critical(monkeypatch: Any) -> None:
    from app.repositories.data_quality.trust import REQUIRED_GLOSSARY_SLUGS

    for slug in REQUIRED_GLOSSARY_SLUGS:
        install_clean_report_fakes(monkeypatch)
        monkeypatch.setattr(
            data_quality_repository,
            "list_missing_required_glossary_terms",
            lambda *_, s=slug: [{"slug": s}],
        )
        report = data_quality.build_data_quality_report(CONNECTION)
        assert any(i.code == "glossary_term_missing" for i in report.issues), (
            f"no issue for {slug}"
        )
        assert report.valid is False, f"expected valid=False for missing slug {slug}"
