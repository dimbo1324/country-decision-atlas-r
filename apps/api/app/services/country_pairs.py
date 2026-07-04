from app.core.errors import api_error
from app.core.locales import validate_locale
from app.repositories import (
    countries as countries_repository,
    country_pairs as repository,
)
from app.schemas.common import locale_resolution
from app.schemas.country_pairs import (
    CompatibilityConfidence,
    CompatibilityFreshness,
    CompatibilityLabel,
    CountryPairCompatibility,
    CountryPairCompatibilityListItem,
    CountryPairCompatibilityListResponse,
    CountryPairCompatibilityResponse,
    CountryPairCompatibilitySummary,
    CountryPairCountry,
    CountryPairEvidenceRef,
    CountryPairNote,
    CountryPairSourceRef,
)
from psycopg import Connection
from typing import Any, cast


DISCLAIMER_EN = (
    "This is not legal, tax, immigration, or banking advice. Verify every note "
    "with qualified professionals before acting."
)
DISCLAIMER_RU = (
    "Это не юридическая, налоговая, миграционная или банковская консультация. "
    "Проверяйте каждый пункт у квалифицированных специалистов перед принятием решений."
)

_NOTE_FIELDS: tuple[tuple[str, str], ...] = (
    ("visa_note", "visa"),
    ("banking_note", "banking"),
    ("tax_treaty_note", "tax"),
    ("flight_logistics_note", "flight_logistics"),
    ("timezone_note", "timezone"),
    ("language_note", "language"),
    ("migration_restriction_note", "migration_restriction"),
)


def _disclaimer(locale: str) -> str:
    return DISCLAIMER_RU if locale == "ru" else DISCLAIMER_EN


def _country_locale(locale: str) -> Any:
    status = "source" if locale == "en" else "fallback"
    return locale_resolution(locale, locale if locale == "en" else "en", status)


def _origin_ref(row: dict[str, Any]) -> CountryPairCountry:
    return CountryPairCountry(
        slug=str(row["origin_slug"]),
        name=str(row["origin_name"]),
        iso2=row.get("origin_iso2"),
    )


def _destination_ref(row: dict[str, Any]) -> CountryPairCountry:
    return CountryPairCountry(
        slug=str(row["destination_slug"]),
        name=str(row["destination_name"]),
        iso2=row.get("destination_iso2"),
    )


def _compatibility_model(row: dict[str, Any]) -> CountryPairCompatibility:
    return CountryPairCompatibility(
        label=cast(CompatibilityLabel, row["compatibility_label"]),
        confidence=cast(CompatibilityConfidence, row["confidence"]),
        freshness_status=cast(CompatibilityFreshness, row["freshness_status"]),
        visa_note=row.get("visa_note"),
        tax_treaty_note=row.get("tax_treaty_note"),
        banking_note=row.get("banking_note"),
        flight_logistics_note=row.get("flight_logistics_note"),
        timezone_note=row.get("timezone_note"),
        language_note=row.get("language_note"),
        migration_restriction_note=row.get("migration_restriction_note"),
        practical_summary=row.get("practical_summary"),
        last_verified_at=row.get("last_verified_at"),
    )


def _key_notes(row: dict[str, Any]) -> list[CountryPairNote]:
    return [
        CountryPairNote(type=note_type, message=str(row[field]))
        for field, note_type in _NOTE_FIELDS
        if row.get(field)
    ]


def _ensure_country_exists(
    connection: Connection[Any], country_slug: str, locale: str
) -> None:
    if (
        countries_repository.get_country(connection, country_slug, locale)
        is None
    ):
        raise api_error(
            404,
            "country_not_found",
            "Country was not found.",
            {"country_slug": country_slug},
        )


def get_country_pair_context(
    connection: Connection[Any],
    origin_slug: str,
    destination_slug: str,
    locale: str,
) -> CountryPairCompatibilityResponse:
    requested_locale = validate_locale(locale)
    _ensure_country_exists(connection, origin_slug, requested_locale)
    _ensure_country_exists(connection, destination_slug, requested_locale)
    row = repository.get_country_pair_compatibility(
        connection, origin_slug, destination_slug
    )
    if row is None:
        raise api_error(
            404,
            "country_pair_not_found",
            "Country pair compatibility was not found.",
            {"origin_slug": origin_slug, "destination_slug": destination_slug},
        )
    sources = repository.list_pair_sources(connection, row["id"])
    evidence = repository.list_pair_evidence(connection, row["id"])
    return CountryPairCompatibilityResponse(
        origin_country=_origin_ref(row),
        destination_country=_destination_ref(row),
        compatibility=_compatibility_model(row),
        sources=[CountryPairSourceRef(**item) for item in sources],
        evidence=[CountryPairEvidenceRef(**item) for item in evidence],
        disclaimer=_disclaimer(requested_locale),
        locale=_country_locale(requested_locale),
    )


def list_destination_pair_contexts(
    connection: Connection[Any], origin_slug: str, locale: str
) -> CountryPairCompatibilityListResponse:
    requested_locale = validate_locale(locale)
    _ensure_country_exists(connection, origin_slug, requested_locale)
    rows = repository.list_destination_compatibility(connection, origin_slug)
    items = []
    for row in rows:
        sources = repository.list_pair_sources(connection, row["id"])
        evidence = repository.list_pair_evidence(connection, row["id"])
        items.append(
            CountryPairCompatibilityListItem(
                destination_country=_destination_ref(row),
                compatibility=_compatibility_model(row),
                sources=[CountryPairSourceRef(**item) for item in sources],
                evidence=[CountryPairEvidenceRef(**item) for item in evidence],
            )
        )
    origin_country = (
        _origin_ref(rows[0])
        if rows
        else _fallback_origin_ref(connection, origin_slug, requested_locale)
    )
    return CountryPairCompatibilityListResponse(
        origin_country=origin_country,
        items=items,
        disclaimer=_disclaimer(requested_locale),
        locale=_country_locale(requested_locale),
    )


def _fallback_origin_ref(
    connection: Connection[Any], origin_slug: str, locale: str
) -> CountryPairCountry:
    country = countries_repository.get_country(connection, origin_slug, locale)
    if country is None:
        raise api_error(
            404,
            "country_not_found",
            "Country was not found.",
            {"country_slug": origin_slug},
        )
    return CountryPairCountry(
        slug=str(country["slug"]),
        name=str(country["name"]),
        iso2=country.get("iso2"),
    )


def build_country_pair_summary(
    row: dict[str, Any],
) -> CountryPairCompatibilitySummary:
    source_ids = row.get("source_ids") or []
    return CountryPairCompatibilitySummary(
        origin_slug=str(row["origin_slug"]),
        destination_slug=str(row["destination_slug"]),
        compatibility_label=cast(
            CompatibilityLabel, row["compatibility_label"]
        ),
        confidence=cast(CompatibilityConfidence, row["confidence"]),
        freshness_status=cast(CompatibilityFreshness, row["freshness_status"]),
        practical_summary=row.get("practical_summary"),
        key_notes=_key_notes(row),
        source_ids=[str(item) for item in source_ids],
    )
