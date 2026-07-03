"""Edge cases for country-pair service helpers: key notes, summaries, disclaimers, empty-result fallback."""

from app.repositories import (
    countries as countries_repository,
    country_pairs as repository,
)
from app.services import country_pairs as service
from fastapi import HTTPException
from psycopg import Connection
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())


def _row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "pair-1",
        "origin_slug": "russia",
        "origin_name": "Russia",
        "origin_iso2": "RU",
        "destination_slug": "uruguay",
        "destination_name": "Uruguay",
        "destination_iso2": "UY",
        "compatibility_label": "favourable",
        "confidence": "medium",
        "freshness_status": "current",
        "visa_note": None,
        "tax_treaty_note": None,
        "banking_note": None,
        "flight_logistics_note": None,
        "timezone_note": None,
        "language_note": None,
        "migration_restriction_note": None,
        "practical_summary": None,
        "last_verified_at": None,
    }
    row.update(overrides)
    return row


class TestKeyNotes:
    def test_only_populated_notes_are_included(self) -> None:
        row = _row(visa_note="Visa-free for 90 days", banking_note="")
        notes = service._key_notes(row)
        assert len(notes) == 1
        assert notes[0].type == "visa"
        assert notes[0].message == "Visa-free for 90 days"

    def test_no_notes_present_returns_empty_list(self) -> None:
        assert service._key_notes(_row()) == []

    def test_all_note_fields_populated_preserves_declared_order(self) -> None:
        row = _row(
            visa_note="visa",
            banking_note="bank",
            tax_treaty_note="tax",
            flight_logistics_note="flight",
            timezone_note="tz",
            language_note="lang",
            migration_restriction_note="restriction",
        )
        notes = service._key_notes(row)
        assert [note.type for note in notes] == [
            "visa",
            "banking",
            "tax",
            "flight_logistics",
            "timezone",
            "language",
            "migration_restriction",
        ]


class TestBuildCountryPairSummary:
    def test_summary_defaults_source_ids_to_empty_list_when_missing(self) -> None:
        summary = service.build_country_pair_summary(_row())
        assert summary.source_ids == []

    def test_summary_stringifies_source_ids(self) -> None:
        summary = service.build_country_pair_summary(_row(source_ids=[1, 2]))
        assert summary.source_ids == ["1", "2"]

    def test_summary_includes_key_notes(self) -> None:
        summary = service.build_country_pair_summary(_row(visa_note="Visa-free"))
        assert any(note.type == "visa" for note in summary.key_notes)


class TestDisclaimerLocale:
    def test_ru_locale_uses_russian_disclaimer(self) -> None:
        assert service._disclaimer("ru") == service.DISCLAIMER_RU

    def test_non_ru_locale_uses_english_disclaimer(self) -> None:
        assert service._disclaimer("en") == service.DISCLAIMER_EN


class TestListDestinationEmptyFallback:
    def test_empty_rows_falls_back_to_direct_country_lookup(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            countries_repository,
            "get_country",
            lambda *_a, **_kw: {"slug": "russia", "name": "Russia", "iso2": "RU"},
        )
        monkeypatch.setattr(
            repository, "list_destination_compatibility", lambda *_a, **_kw: []
        )

        result = service.list_destination_pair_contexts(CONNECTION, "russia", "en")
        assert result.origin_country.slug == "russia"
        assert result.items == []

    def test_empty_rows_and_unknown_origin_raises_404(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls = {"n": 0}

        def fake_get_country(*_a: Any, **_kw: Any) -> dict[str, Any] | None:
            calls["n"] += 1
            if calls["n"] == 1:
                return {"slug": "atlantis", "name": "Atlantis"}
            return None

        monkeypatch.setattr(countries_repository, "get_country", fake_get_country)
        monkeypatch.setattr(
            repository, "list_destination_compatibility", lambda *_a, **_kw: []
        )

        with pytest.raises(HTTPException) as exc_info:
            service.list_destination_pair_contexts(CONNECTION, "atlantis", "en")
        assert exc_info.value.status_code == 404
