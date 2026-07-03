from app.core.errors import api_error
from app.repositories import decision_engine as repository
from app.schemas.common import (
    LocaleResolution,
    Pagination,
    SortMeta,
    source_locale_resolution,
)
from app.schemas.decision_engine import (
    CountryCardResponse,
    DecisionCountryScore,
    EvidenceListResponse,
    LegalSignalDetailResponse,
    SourceListWithLocaleResponse,
    UserStoryCreate,
    UserStoryListResponse,
    UserStoryResponse,
)
from app.schemas.sources import EvidenceItemListResponse
from app.services.decision_engine import helpers
from psycopg import Connection
from typing import Any


def get_country_card(
    connection: Connection[Any], country_slug: str, locale: str
) -> CountryCardResponse:
    row = repository.get_country_card(connection, country_slug, locale)
    if row is None:
        raise LookupError("Country card not found")
    return CountryCardResponse(item=row, locale=helpers._locale([row], locale))


def get_scenario(connection: Connection[Any], slug: str, locale: str) -> dict[str, Any]:
    row = repository.get_scenario(connection, slug, locale)
    if row is None:
        raise LookupError("Scenario not found")
    return row


def list_scenario_countries(
    connection: Connection[Any], scenario_slug: str, locale: str
) -> list[DecisionCountryScore]:
    rows = repository.list_scenario_countries(connection, scenario_slug)
    rows = helpers.overlay_localized_fields(
        connection,
        rows,
        "scenario",
        "scenario_id",
        [("title", "scenario_name", "title_ru", "title_en")],
        locale,
    )
    rows = helpers.overlay_localized_fields(
        connection,
        rows,
        "country_score",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    return helpers._attach_breakdowns_and_sources(connection, rows, locale)


def get_country_sources(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    limit: int,
    offset: int,
    source_type: str | None = None,
    language: str | None = None,
    confidence: str | None = None,
    status: str = "published",
    sort: str = "title",
    order: str = "asc",
) -> SourceListWithLocaleResponse:
    rows = repository.list_country_sources(
        connection,
        country_slug,
        limit,
        offset,
        source_type,
        language,
        confidence,
        status,
        sort,
        order,
    )
    total = repository.count_country_sources(
        connection, country_slug, source_type, language, confidence, status
    )
    return SourceListWithLocaleResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
        locale=source_locale_resolution(locale),
    )


def list_legal_signals(
    connection: Connection[Any],
    locale: str,
    country_slug: str | None,
    limit: int,
    offset: int,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
    sort: str = "published_date",
    order: str = "desc",
) -> tuple[list[dict[str, Any]], Pagination, LocaleResolution, SortMeta]:
    rows = repository.list_legal_signals(
        connection=connection,
        country_slug=country_slug,
        signal_type=signal_type,
        impact_direction=impact_direction,
        impact_level=impact_level,
        status=status,
        limit=limit,
        offset=offset,
        sort=sort,
        order=order,
    )
    rows = helpers.overlay_localized_fields(
        connection,
        rows,
        "legal_signal",
        "id",
        [
            ("title", "title", "title_ru", "title_en"),
            ("summary", "summary", "summary_ru", "summary_en"),
        ],
        locale,
    )
    total = repository.count_legal_signals(
        connection,
        country_slug,
        signal_type,
        impact_direction,
        impact_level,
        status,
    )
    return (
        rows,
        Pagination(limit=limit, offset=offset, total=total),
        helpers._locale(rows, locale),
        SortMeta(sort=sort, order=order),
    )


def get_legal_signal(
    connection: Connection[Any], signal_id: str, locale: str
) -> LegalSignalDetailResponse:
    row = repository.get_legal_signal(connection, signal_id, locale)
    if row is None:
        raise LookupError("Legal signal not found")
    return LegalSignalDetailResponse(item=row, locale=helpers._locale([row], locale))


def get_legal_signal_evidence(
    connection: Connection[Any], signal_id: str
) -> EvidenceListResponse:
    rows = repository.list_evidence_for_legal_signal(connection, signal_id)
    return EvidenceListResponse(
        items=rows,
        pagination=Pagination(limit=len(rows) or 1, offset=0, total=len(rows)),
    )


def get_source(connection: Connection[Any], source_id: str) -> dict[str, Any]:
    row = repository.get_source(connection, source_id)
    if row is None:
        raise LookupError("Source not found")
    return row


def get_source_evidence(
    connection: Connection[Any], source_id: str, limit: int, offset: int
) -> EvidenceItemListResponse:
    rows = repository.list_evidence_for_source(connection, source_id, limit, offset)
    total = repository.count_evidence_for_source(connection, source_id)
    return EvidenceItemListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


def list_user_stories(
    connection: Connection[Any],
    limit: int,
    offset: int,
    origin_country_slug: str | None = None,
    destination_country_slug: str | None = None,
    scenario: str | None = None,
    verification_status: str | None = None,
    is_synthetic: bool | None = None,
    status: str = "published",
    sort: str = "created_at",
    order: str = "desc",
) -> UserStoryListResponse:
    rows = repository.list_user_stories(
        connection,
        limit,
        offset,
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
        sort,
        order,
    )
    total = repository.count_user_stories(
        connection,
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
    )
    return UserStoryListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
    )


def get_user_story(connection: Connection[Any], story_id: str) -> UserStoryResponse:
    row = repository.get_user_story(connection, story_id)
    if row is None:
        raise LookupError("User story not found")
    return UserStoryResponse(item=row)


def create_user_story(
    connection: Connection[Any], payload: UserStoryCreate
) -> UserStoryResponse:
    if payload.origin_country_slug and not repository.active_country_exists(
        connection, payload.origin_country_slug
    ):
        raise api_error(
            422,
            "user_story_country_invalid",
            "Origin country does not exist or is inactive.",
            {"field": "origin_country_slug"},
        )
    if not repository.active_country_exists(
        connection, payload.destination_country_slug
    ):
        raise api_error(
            422,
            "user_story_country_invalid",
            "Destination country does not exist or is inactive.",
            {"field": "destination_country_slug"},
        )
    if not repository.active_scenario_exists(connection, payload.scenario):
        raise api_error(
            422,
            "user_story_scenario_invalid",
            "Scenario does not exist or is inactive.",
            {"field": "scenario"},
        )
    row = repository.create_user_story(connection, payload)
    connection.commit()
    return UserStoryResponse(item=row)
