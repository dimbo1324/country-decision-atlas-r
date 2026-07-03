"""Data-quality checks for published routes: missing sources, titles, and summaries."""

from app.repositories import data_quality as repo
from app.services import data_quality as service
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())

ROUTE_ROW: dict[str, Any] = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "slug": "temporary-residence",
    "route_type": "temporary_residence",
    "country_slug": "uruguay",
}

MISMATCH_SOURCE_ROW: dict[str, Any] = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "slug": "temporary-residence",
    "country_slug": "uruguay",
    "source_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "source_country_slug": "russia",
}

MISMATCH_EVIDENCE_ROW: dict[str, Any] = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "slug": "temporary-residence",
    "country_slug": "uruguay",
    "evidence_item_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
    "evidence_country_slug": "russia",
}

MISSING_TEXT_ROW: dict[str, Any] = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "slug": "incomplete-route",
    "route_type": "temporary_residence",
    "country_slug": "uruguay",
    "missing_field": "summary",
}

LEGAL_STATUS_ROW: dict[str, Any] = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "slug": "temporary-residence",
    "route_type": "temporary_residence",
    "country_slug": "uruguay",
    "legal_status": "unknown",
}


def test_published_route_without_source_is_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [ROUTE_ROW])
    result = repo.list_published_routes_without_sources(CONNECTION)
    assert len(result) == 1
    assert result[0]["slug"] == "temporary-residence"


def test_published_route_with_source_is_not_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [])
    result = repo.list_published_routes_without_sources(CONNECTION)
    assert result == []


def test_published_route_missing_title_is_returned(monkeypatch: Any) -> None:
    row = {**MISSING_TEXT_ROW, "missing_field": "title"}
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [row])
    result = repo.list_published_routes_missing_required_text(CONNECTION)
    assert len(result) == 1
    assert result[0]["missing_field"] == "title"


def test_published_route_missing_summary_is_returned(monkeypatch: Any) -> None:
    row = {**MISSING_TEXT_ROW, "missing_field": "summary"}
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [row])
    result = repo.list_published_routes_missing_required_text(CONNECTION)
    assert len(result) == 1
    assert result[0]["missing_field"] == "summary"


def test_published_route_missing_eligibility_summary_is_returned(
    monkeypatch: Any,
) -> None:
    row = {**MISSING_TEXT_ROW, "missing_field": "eligibility_summary"}
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [row])
    result = repo.list_published_routes_missing_required_text(CONNECTION)
    assert len(result) == 1
    assert result[0]["missing_field"] == "eligibility_summary"


def test_route_with_all_eligibility_unknown_is_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [ROUTE_ROW])
    result = repo.list_published_routes_with_all_eligibility_unknown(CONNECTION)
    assert len(result) == 1


def test_route_without_documents_is_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [ROUTE_ROW])
    result = repo.list_published_routes_without_documents(CONNECTION)
    assert len(result) == 1
    assert result[0]["slug"] == "temporary-residence"


def test_route_source_country_mismatch_is_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [MISMATCH_SOURCE_ROW])
    result = repo.list_route_source_country_mismatches(CONNECTION)
    assert len(result) == 1
    assert result[0]["source_country_slug"] == "russia"
    assert result[0]["country_slug"] == "uruguay"


def test_route_evidence_country_mismatch_is_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [MISMATCH_EVIDENCE_ROW])
    result = repo.list_route_evidence_country_mismatches(CONNECTION)
    assert len(result) == 1
    assert result[0]["evidence_country_slug"] == "russia"
    assert result[0]["country_slug"] == "uruguay"


def test_route_with_unknown_legal_status_is_returned(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [LEGAL_STATUS_ROW])
    result = repo.list_published_routes_with_unknown_legal_status(CONNECTION)
    assert len(result) == 1
    assert result[0]["legal_status"] == "unknown"


def test_published_route_missing_source_produces_critical_issue(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_published_routes_without_sources",
        lambda *_: [ROUTE_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "published_route_missing_source" in codes
    sevs = {
        i.severity for i in report.issues if i.code == "published_route_missing_source"
    }
    assert sevs == {"critical"}
    assert report.valid is False


def test_published_route_missing_required_text_produces_critical_issue(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_published_routes_missing_required_text",
        lambda *_: [MISSING_TEXT_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "published_route_missing_required_text" in codes
    sevs = {
        i.severity
        for i in report.issues
        if i.code == "published_route_missing_required_text"
    }
    assert sevs == {"critical"}
    assert report.valid is False


def test_route_source_country_mismatch_produces_critical_issue(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_route_source_country_mismatches",
        lambda *_: [MISMATCH_SOURCE_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "route_source_country_mismatch" in codes
    sevs = {
        i.severity for i in report.issues if i.code == "route_source_country_mismatch"
    }
    assert sevs == {"critical"}
    assert report.valid is False


def test_route_evidence_country_mismatch_produces_critical_issue(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_route_evidence_country_mismatches",
        lambda *_: [MISMATCH_EVIDENCE_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "route_evidence_country_mismatch" in codes
    sevs = {
        i.severity for i in report.issues if i.code == "route_evidence_country_mismatch"
    }
    assert sevs == {"critical"}
    assert report.valid is False


def test_published_route_missing_legal_status_produces_critical_issue(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_published_routes_missing_legal_status",
        lambda *_: [ROUTE_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "published_route_missing_legal_status" in codes
    sevs = {
        i.severity
        for i in report.issues
        if i.code == "published_route_missing_legal_status"
    }
    assert sevs == {"critical"}
    assert report.valid is False


def test_all_eligibility_unknown_produces_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_published_routes_with_all_eligibility_unknown",
        lambda *_: [ROUTE_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "published_route_all_eligibility_unknown" in codes
    sevs = {
        i.severity
        for i in report.issues
        if i.code == "published_route_all_eligibility_unknown"
    }
    assert sevs == {"warning"}
    assert report.valid is True


def test_missing_documents_produces_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_published_routes_without_documents",
        lambda *_: [ROUTE_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "published_route_missing_documents" in codes
    sevs = {
        i.severity
        for i in report.issues
        if i.code == "published_route_missing_documents"
    }
    assert sevs == {"warning"}
    assert report.valid is True


def test_legal_status_unknown_produces_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repo,
        "list_published_routes_with_unknown_legal_status",
        lambda *_: [LEGAL_STATUS_ROW],
    )

    report = service.build_data_quality_report(CONNECTION)

    codes = {i.code for i in report.issues}
    assert "published_route_legal_status_unknown" in codes
    sevs = {
        i.severity
        for i in report.issues
        if i.code == "published_route_legal_status_unknown"
    }
    assert sevs == {"warning"}
    assert report.valid is True


def test_clean_routes_produce_no_critical_route_issues(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)

    report = service.build_data_quality_report(CONNECTION)

    route_critical_codes = {
        "published_route_missing_source",
        "published_route_missing_required_text",
        "route_source_country_mismatch",
        "route_evidence_country_mismatch",
        "published_route_missing_legal_status",
    }
    actual_codes = {i.code for i in report.issues}
    assert actual_codes.isdisjoint(route_critical_codes)
    assert report.valid is True


def test_route_dq_check_codes_present_in_report(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)

    report = service.build_data_quality_report(CONNECTION)

    check_codes = {c.code for c in report.checks}
    expected = {
        "published_routes_have_sources",
        "published_routes_have_required_text",
        "route_sources_match_route_country",
        "route_evidence_matches_route_country",
        "published_routes_have_legal_status",
        "published_routes_quality",
    }
    assert expected.issubset(check_codes)
