import pytest
from unittest.mock import MagicMock, patch


COUNTRY_SLUG = "germany"
LOCALE_RU = "ru"
LOCALE_EN = "en"


def _mock_connection():
    conn = MagicMock()
    conn.execute.return_value = MagicMock()
    return conn


@pytest.fixture
def mock_variants_empty():
    return {}


@pytest.fixture
def mock_variant_ru_original():
    return {
        ("entity-1", "title"): {
            "translation_unit_id": "unit-1",
            "entity_id": "entity-1",
            "field_name": "title",
            "original_locale_code": "ru",
            "unit_source_hash": "abc123",
            "translation_variant_id": "variant-1",
            "locale_code": "ru",
            "text": "Тестовый заголовок",
            "status": "human_authored",
            "method": None,
            "source_locale_code": "ru",
            "source_hash": "abc123",
            "is_original": True,
            "quality_score": None,
        }
    }


@pytest.fixture
def mock_variant_en_translated():
    return {
        ("entity-1", "title"): {
            "translation_unit_id": "unit-1",
            "entity_id": "entity-1",
            "field_name": "title",
            "original_locale_code": "ru",
            "unit_source_hash": "abc123",
            "translation_variant_id": "variant-2",
            "locale_code": "en",
            "text": "Test Title",
            "status": "human_reviewed",
            "method": "human",
            "source_locale_code": "ru",
            "source_hash": "abc123",
            "is_original": False,
            "quality_score": 0.95,
        }
    }


@pytest.fixture
def mock_variant_stale():
    return {
        ("entity-1", "title"): {
            "translation_unit_id": "unit-1",
            "entity_id": "entity-1",
            "field_name": "title",
            "original_locale_code": "ru",
            "unit_source_hash": "abc123",
            "translation_variant_id": "variant-2",
            "locale_code": "en",
            "text": "Outdated Title",
            "status": "human_reviewed",
            "method": "human",
            "source_locale_code": "ru",
            "source_hash": "stale999",
            "is_original": False,
            "quality_score": 0.9,
        }
    }


class TestCountryCardLocalizationMeta:
    def test_country_card_localization_present(self, mock_variant_ru_original):
        from app.services.localization import overlay_localized_fields

        items = [{"id": "entity-1", "title": "Old Title"}]
        conn = _mock_connection()
        with patch(
            "app.repositories.translations.list_best_translation_variants",
            return_value=mock_variant_ru_original,
        ):
            result = overlay_localized_fields(
                conn, items, "country_card", "id", [("title", "title", None, None)], "ru"
            )
        loc = result[0].get("localization")
        assert loc is not None
        assert loc["requested_locale"] == "ru"
        assert loc["resolved_locale"] == "ru"
        assert len(loc["fields"]) == 1
        assert loc["fields"][0]["field_name"] == "title"


class TestRuOriginal:
    def test_ru_original_status_and_flags(self, mock_variant_ru_original):
        from app.services.localization import field_meta_from_variant

        variant = mock_variant_ru_original[("entity-1", "title")]
        meta = field_meta_from_variant("title", "ru", variant)
        assert meta.is_original is True
        assert meta.is_fallback is False
        assert meta.is_stale is False
        assert meta.translation_unit_id == "unit-1"
        assert meta.translation_variant_id == "variant-1"


class TestEnFallback:
    def test_en_fallback_when_no_en_variant(self, mock_variant_ru_original):
        from app.services.localization import overlay_localized_fields

        items = [{"id": "entity-1", "title": "Old", "title_en": None, "title_ru": "Заголовок"}]
        conn = _mock_connection()
        with patch(
            "app.repositories.translations.list_best_translation_variants",
            return_value={},
        ):
            result = overlay_localized_fields(
                conn,
                items,
                "country_card",
                "id",
                [("title", "title", "title_ru", "title_en")],
                "en",
            )
        loc = result[0].get("localization")
        assert loc is not None
        field = loc["fields"][0]
        assert field["is_fallback"] is True
        assert field["method"] == "legacy"


class TestStaleDetection:
    def test_stale_flag_set_when_hashes_differ(self, mock_variant_stale):
        from app.services.localization import field_meta_from_variant

        variant = mock_variant_stale[("entity-1", "title")]
        meta = field_meta_from_variant("title", "en", variant)
        assert meta.is_stale is True
        assert meta.is_original is False


class TestMissingFields:
    def test_missing_field_status_and_meta(self):
        from app.services.localization import overlay_localized_fields

        items = [{"id": "entity-1", "title": None}]
        conn = _mock_connection()
        with patch(
            "app.repositories.translations.list_best_translation_variants",
            return_value={},
        ):
            result = overlay_localized_fields(
                conn, items, "country_card", "id", [("title", "title", None, None)], "en"
            )
        loc = result[0].get("localization")
        assert loc is not None
        assert "title" in loc["missing_fields"]


class TestLegacyFallback:
    def test_legacy_method_used_when_no_unit(self):
        from app.services.localization import legacy_field_meta

        meta = legacy_field_meta("summary", "en", "ru", "fallback")
        assert meta.method == "legacy"
        assert meta.translation_unit_id is None
        assert meta.translation_variant_id is None
        assert meta.is_fallback is True


class TestBuildLocalizationMeta:
    def test_aggregate_status_priority(self):
        from app.services.localization import build_localization_meta
        from app.schemas.localization import TranslationFieldMeta

        metas = [
            TranslationFieldMeta(
                field_name="title",
                requested_locale="en",
                resolved_locale="en",
                source_locale="ru",
                status="human_reviewed",
                method="human",
                is_original=False,
                is_fallback=False,
                is_stale=False,
            ),
            TranslationFieldMeta(
                field_name="summary",
                requested_locale="en",
                resolved_locale="ru",
                source_locale="ru",
                status="fallback",
                method="legacy",
                is_original=True,
                is_fallback=True,
                is_stale=False,
            ),
        ]
        loc = build_localization_meta("en", metas)
        assert loc.is_fallback is True
        assert loc.status == "fallback"
        assert loc.has_stale_fields is False


class TestLegalSignalLocalization:
    def test_legal_signal_overlay_adds_localization(self):
        from app.services.localization import overlay_localized_fields

        items = [
            {
                "id": "signal-1",
                "title": "Старый заголовок",
                "summary": "Резюме",
                "title_ru": "Новый заголовок",
                "title_en": None,
                "summary_ru": "Новое резюме",
                "summary_en": None,
            }
        ]
        conn = _mock_connection()
        with patch(
            "app.repositories.translations.list_best_translation_variants",
            return_value={},
        ):
            result = overlay_localized_fields(
                conn,
                items,
                "legal_signal",
                "id",
                [
                    ("title", "title", "title_ru", "title_en"),
                    ("summary", "summary", "summary_ru", "summary_en"),
                ],
                "ru",
            )
        assert result[0].get("localization") is not None
        assert len(result[0]["localization"]["fields"]) == 2


class TestSourceLocalization:
    def test_source_overlay_title_notes(self):
        from app.services.localization import overlay_localized_fields

        items = [{"id": "src-1", "title": "Source Title", "notes": None}]
        conn = _mock_connection()
        with patch(
            "app.repositories.translations.list_best_translation_variants",
            return_value={},
        ):
            result = overlay_localized_fields(
                conn,
                items,
                "source",
                "id",
                [
                    ("title", "title", None, None),
                    ("notes", "notes", None, None),
                ],
                "en",
            )
        loc = result[0].get("localization")
        assert loc is not None
        field_names = [f["field_name"] for f in loc["fields"]]
        assert "title" in field_names
        assert "notes" in field_names


class TestDecisionLocalization:
    def test_decision_run_response_schema_accepts_localization(self):
        from app.schemas.decision_engine import DecisionCountryResult, DecisionCountryRef, DecisionBreakdownItem, DecisionSourceRef
        from app.schemas.localization import LocalizationMeta

        loc = LocalizationMeta(
            requested_locale="en",
            resolved_locale="ru",
            status="fallback",
            is_fallback=True,
            has_machine_translation=False,
            has_human_review=False,
            has_stale_fields=False,
        )
        result = DecisionCountryResult(
            rank=1,
            country=DecisionCountryRef(id="c1", slug="germany", name="Germany"),
            score=0.8,
            score_label="strong",
            summary="Good country",
            strengths=[],
            weaknesses=[],
            risk_warnings=[],
            confidence="high",
            breakdown=[],
            sources=[],
            localization=loc,
        )
        assert result.localization is not None
        assert result.localization.status == "fallback"
