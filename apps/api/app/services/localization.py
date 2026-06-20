from app.core.locales import AUTHORING_LOCALE, validate_locale
from app.repositories import translations as repository
from app.schemas.localization import LocalizedText, TranslationMeta
from psycopg import Connection
from typing import Any


def resolve_localized_text(
    connection: Connection[Any],
    entity_type: str,
    entity_id: str,
    field_name: str,
    requested_locale: str,
    fallback_locale: str = AUTHORING_LOCALE,
) -> LocalizedText | None:
    resolved_requested_locale = validate_locale(requested_locale)
    resolved_fallback_locale = validate_locale(fallback_locale)
    variant = repository.get_best_translation_variant(
        connection,
        entity_type,
        entity_id,
        field_name,
        resolved_requested_locale,
        resolved_fallback_locale,
    )
    if variant is None:
        return None
    resolved_locale = str(variant["locale_code"])
    source_locale = str(
        variant.get("source_locale_code")
        or variant.get("original_locale_code")
        or resolved_locale
    )
    is_fallback = resolved_locale != resolved_requested_locale
    is_original = bool(variant["is_original"])
    is_stale = not is_original and variant.get("source_hash") != variant.get(
        "unit_source_hash"
    )
    return LocalizedText(
        text=str(variant["text"]),
        meta=TranslationMeta(
            requested_locale=resolved_requested_locale,
            resolved_locale=resolved_locale,
            source_locale=source_locale,
            status="fallback" if is_fallback else str(variant["status"]),
            method=str(variant["method"]) if variant.get("method") else None,
            is_original=is_original,
            is_fallback=is_fallback,
            is_stale=is_stale,
            quality_score=(
                float(variant["quality_score"])
                if variant.get("quality_score") is not None
                else None
            ),
        ),
    )
