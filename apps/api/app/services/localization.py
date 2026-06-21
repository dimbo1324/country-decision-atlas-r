from app.core.locales import AUTHORING_LOCALE, validate_locale
from app.repositories import translations as repository
from app.schemas.localization import (
    LocalizationMeta,
    LocalizedText,
    TranslationFieldMeta,
    TranslationMeta,
)
from psycopg import Connection
from typing import Any


_STATUS_DEGRADATION_RANK: dict[str, int] = {
    "source": 0,
    "translated": 1,
    "fallback": 2,
    "missing": 3,
}


def _worse_status(a: str | None, b: str) -> str:
    if a is None:
        return b
    return (
        a
        if _STATUS_DEGRADATION_RANK.get(a, 3) >= _STATUS_DEGRADATION_RANK.get(b, 3)
        else b
    )


def field_meta_from_variant(
    field_name: str,
    requested_locale: str,
    variant: dict[str, Any],
) -> TranslationFieldMeta:
    resolved_locale = str(variant["locale_code"])
    source_locale = str(
        variant.get("source_locale_code")
        or variant.get("original_locale_code")
        or resolved_locale
    )
    is_fallback = resolved_locale != requested_locale
    is_original = bool(variant.get("is_original"))
    is_stale = (
        not is_original
        and variant.get("source_hash") is not None
        and variant.get("unit_source_hash") is not None
        and variant.get("source_hash") != variant.get("unit_source_hash")
    )
    status = "fallback" if is_fallback else str(variant["status"])
    return TranslationFieldMeta(
        field_name=field_name,
        requested_locale=requested_locale,
        resolved_locale=resolved_locale,
        source_locale=source_locale,
        status=status,
        method=str(variant["method"]) if variant.get("method") else None,
        is_original=is_original,
        is_fallback=is_fallback,
        is_stale=bool(is_stale),
        translation_unit_id=variant.get("translation_unit_id"),
        translation_variant_id=variant.get("translation_variant_id"),
        quality_score=(
            float(variant["quality_score"])
            if variant.get("quality_score") is not None
            else None
        ),
    )


def legacy_field_meta(
    field_name: str,
    requested_locale: str,
    resolved_locale: str,
    status: str,
) -> TranslationFieldMeta:
    is_fallback = resolved_locale != requested_locale
    return TranslationFieldMeta(
        field_name=field_name,
        requested_locale=requested_locale,
        resolved_locale=resolved_locale,
        source_locale=resolved_locale,
        status=status,
        method="legacy",
        is_original=status in ("original", "source"),
        is_fallback=is_fallback,
        is_stale=False,
        translation_unit_id=None,
        translation_variant_id=None,
        quality_score=None,
    )


def build_localization_meta(
    requested_locale: str,
    field_metas: list[TranslationFieldMeta],
) -> LocalizationMeta:
    if not field_metas:
        return LocalizationMeta(
            requested_locale=requested_locale,
            resolved_locale=requested_locale,
            status="missing",
            is_fallback=False,
            has_machine_translation=False,
            has_human_review=False,
            has_stale_fields=False,
            missing_fields=[],
            stale_fields=[],
            fields=[],
        )
    stale_fields = [m.field_name for m in field_metas if m.is_stale]
    missing_fields = [m.field_name for m in field_metas if m.status == "missing"]
    has_fallback = any(m.is_fallback for m in field_metas)
    has_machine = any(
        m.status == "machine_translated" or m.method == "machine" for m in field_metas
    )
    has_human_review = any(m.status == "human_reviewed" for m in field_metas)

    if missing_fields:
        status = "missing"
    elif stale_fields:
        status = "stale"
    elif has_fallback:
        status = "fallback"
    elif has_human_review:
        status = "human_reviewed"
    elif has_machine:
        status = "machine_translated"
    elif all(m.is_original for m in field_metas):
        status = "original"
    else:
        status = "human_authored"

    resolved_locale = (
        requested_locale
        if not has_fallback and not missing_fields
        else field_metas[0].resolved_locale
    )
    return LocalizationMeta(
        requested_locale=requested_locale,
        resolved_locale=resolved_locale,
        status=status,
        is_fallback=has_fallback,
        has_machine_translation=has_machine,
        has_human_review=has_human_review,
        has_stale_fields=bool(stale_fields),
        missing_fields=missing_fields,
        stale_fields=stale_fields,
        fields=field_metas,
    )


def locale_status_from_localization(meta: LocalizationMeta) -> str:
    if meta.status == "missing":
        return "missing"
    if meta.is_fallback:
        return "fallback"
    if meta.status in ("original", "human_authored"):
        return "source"
    return "translated"


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
        field_metas: list[TranslationFieldMeta] = []
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
                meta = field_meta_from_variant(output_key, resolved_requested, variant)
                field_metas.append(meta)
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

                if primary_text is not None:
                    meta_resolved_locale = resolved_fallback
                    meta_status = (
                        "fallback"
                        if meta_resolved_locale != resolved_requested
                        else "original"
                    )
                elif fallback_text is not None:
                    meta_resolved_locale = "en"
                    meta_status = (
                        "fallback" if resolved_requested != "en" else "original"
                    )
                else:
                    meta_resolved_locale = resolved_requested
                    meta_status = "missing"

                leg_meta = legacy_field_meta(
                    output_key, resolved_requested, meta_resolved_locale, meta_status
                )
                field_metas.append(leg_meta)
            worst = _worse_status(worst, field_status)

        new_status = worst or "missing"
        existing_status: str | None = item.get("translation_status") or None
        final_status = _worse_status(existing_status, new_status)
        item["translation_status"] = final_status
        item["resolved_locale"] = (
            resolved_requested if final_status in ("translated", "source") else "en"
        )

        existing_loc = item.get("localization")
        if existing_loc and isinstance(existing_loc, dict):
            existing_field_metas = [
                TranslationFieldMeta.model_validate(f)
                for f in existing_loc.get("fields", [])
            ]
            all_field_metas = existing_field_metas + field_metas
        else:
            all_field_metas = field_metas

        localization = build_localization_meta(resolved_requested, all_field_metas)
        item["localization"] = localization.model_dump(mode="json")

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
