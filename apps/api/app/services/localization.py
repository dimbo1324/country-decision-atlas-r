from app.core.locales import AUTHORING_LOCALE, validate_locale
from app.repositories import translations as repository
from app.schemas.localization import LocalizedText, TranslationMeta
from psycopg import Connection
from typing import Any


_STATUS_PRIORITY: dict[str, int] = {
    "source": 0,
    "translated": 1,
    "fallback": 2,
    "missing": 3,
}


def _worse_status(a: str | None, b: str) -> str:
    if a is None:
        return b
    return a if _STATUS_PRIORITY.get(a, 3) >= _STATUS_PRIORITY.get(b, 3) else b


def overlay_localized_fields(
    connection: Connection[Any],
    items: list[dict[str, Any]],
    entity_type: str,
    entity_id_key: str,
    specs: list[tuple[str, str, str | None, str | None]],
    requested_locale: str,
    fallback_locale: str = AUTHORING_LOCALE,
) -> list[dict[str, Any]]:
    if not items:
        return items
    resolved_requested = validate_locale(requested_locale)
    resolved_fallback = validate_locale(fallback_locale)
    entity_ids = [str(item[entity_id_key]) for item in items]
    field_names = list({spec[0] for spec in specs})
    variants = repository.list_best_translation_variants(
        connection,
        entity_type,
        entity_ids,
        field_names,
        resolved_requested,
        resolved_fallback,
    )
    for item in items:
        entity_id = str(item[entity_id_key])
        worst: str | None = None
        for field_name, output_key, legacy_primary_key, legacy_fallback_key in specs:
            variant = variants.get((entity_id, field_name))
            if variant is not None:
                locale_code = str(variant["locale_code"])
                item[output_key] = str(variant["text"])
                if resolved_requested == "en":
                    field_status = "source"
                elif locale_code == resolved_requested:
                    field_status = "translated"
                else:
                    field_status = "fallback"
            else:
                primary_text: str | None = (
                    item.get(legacy_primary_key) or None if legacy_primary_key else None
                )
                fallback_text: str | None = (
                    item.get(legacy_fallback_key) or None
                    if legacy_fallback_key
                    else None
                )
                text = primary_text or fallback_text
                item[output_key] = text or ""
                if resolved_requested == "en":
                    field_status = "source" if text else "missing"
                elif primary_text:
                    field_status = "translated"
                elif fallback_text:
                    field_status = "fallback"
                else:
                    field_status = "missing"
            worst = _worse_status(worst, field_status)
        new_status = worst or "missing"
        existing_status: str | None = item.get("translation_status") or None
        final_status = _worse_status(existing_status, new_status)
        item["translation_status"] = final_status
        item["resolved_locale"] = (
            resolved_requested if final_status in ("translated", "source") else "en"
        )
    return items


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
