import json
from app.core.database import execute_one, fetch_one
from psycopg import Connection, sql
from typing import Any, cast


SOURCE_RETURNING = """
id,
title,
url,
source_type,
publisher,
country_id,
locale_id,
reliability_level,
language,
confidence,
status,
published_at,
accessed_at,
last_checked_at,
notes,
created_at,
updated_at
"""

EVIDENCE_RETURNING = """
id,
source_id,
country_id,
legal_signal_id,
title,
summary,
url,
quote,
evidence_type,
confidence_level,
claim,
excerpt,
retrieved_at,
confidence,
status,
published_at,
created_at,
updated_at
"""

LEGAL_SIGNAL_RETURNING = """
id,
country_id,
source_id,
title,
summary,
title_en,
title_ru,
summary_en,
summary_ru,
signal_type,
sentiment,
severity,
impact_direction,
impact_level,
affected_groups,
published_date,
effective_date,
confidence,
confidence_level,
status,
legal_status,
published_at,
created_at,
updated_at
"""

COUNTRY_CARD_RETURNING = """
id,
country_id,
locale,
executive_summary,
migration_overview,
tax_overview,
cost_of_living_overview,
business_overview,
safety_overview,
legal_signals_summary,
risk_summary,
source_summary,
status,
created_at,
updated_at
"""

USER_STORY_RETURNING = """
id,
origin_country_id,
destination_country_id,
city,
year,
scenario,
budget_initial_usd,
budget_monthly_usd,
legal_path,
documents_used,
problems,
positive_outcome,
negative_outcome,
advice,
satisfaction_score,
verification_status,
status,
is_synthetic,
notes,
created_at,
updated_at
"""

SOURCE_PATCH_FIELDS = {
    "title",
    "url",
    "source_type",
    "publisher",
    "language",
    "confidence",
    "published_at",
    "last_checked_at",
    "notes",
    "status",
}
EVIDENCE_PATCH_FIELDS = {
    "source_id",
    "legal_signal_id",
    "claim",
    "excerpt",
    "url",
    "confidence",
    "legal_status",
    "status",
}
LEGAL_SIGNAL_PATCH_FIELDS = {
    "source_id",
    "title_en",
    "title_ru",
    "summary_en",
    "summary_ru",
    "signal_type",
    "impact_direction",
    "impact_level",
    "affected_groups",
    "published_date",
    "effective_date",
    "confidence",
    "status",
}
COUNTRY_CARD_PATCH_FIELDS = {
    "executive_summary",
    "migration_overview",
    "tax_overview",
    "cost_of_living_overview",
    "business_overview",
    "safety_overview",
    "legal_signals_summary",
    "risk_summary",
    "source_summary",
    "status",
}
USER_STORY_PATCH_FIELDS = {
    "origin_country_id",
    "destination_country_id",
    "city",
    "year",
    "scenario",
    "budget_initial_usd",
    "budget_monthly_usd",
    "legal_path",
    "documents_used",
    "problems",
    "positive_outcome",
    "negative_outcome",
    "advice",
    "satisfaction_score",
    "verification_status",
    "status",
    "is_synthetic",
    "notes",
}


def get_country_id_by_slug(
    connection: Connection[Any], country_slug: str
) -> str | None:
    row = fetch_one(
        connection,
        "SELECT id::text AS id FROM countries WHERE slug = %s",
        (country_slug,),
    )
    return str(row["id"]) if row else None


def get_country_slug_by_id(
    connection: Connection[Any], country_id: str
) -> str | None:
    row = fetch_one(
        connection,
        "SELECT slug FROM countries WHERE id::text = %s",
        (country_id,),
    )
    return str(row["slug"]) if row else None


def get_source_for_admin(
    connection: Connection[Any], source_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"SELECT {SOURCE_RETURNING} FROM sources WHERE id::text = %s",
        (source_id,),
    )


def create_source(
    connection: Connection[Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO sources (
            country_id,
            title,
            url,
            source_type,
            publisher,
            language,
            reliability_level,
            confidence,
            published_at,
            last_checked_at,
            notes,
            status
        )
        VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING {SOURCE_RETURNING}
        """,
        (
            payload.get("country_id"),
            payload.get("title"),
            payload.get("url"),
            payload.get("source_type"),
            payload.get("publisher"),
            payload.get("language"),
            payload.get("confidence") or "medium",
            payload.get("confidence") or "medium",
            payload.get("published_at"),
            payload.get("last_checked_at"),
            payload.get("notes"),
            payload.get("status"),
        ),
    )


def patch_source(
    connection: Connection[Any],
    source_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    payload = _mirror_source_confidence(payload)
    return _patch_entity(
        connection,
        "sources",
        source_id,
        payload,
        SOURCE_PATCH_FIELDS | {"reliability_level"},
        SOURCE_RETURNING,
    )


def get_evidence_item_for_admin(
    connection: Connection[Any], evidence_item_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"SELECT {EVIDENCE_RETURNING} FROM evidence_items WHERE id::text = %s",
        (evidence_item_id,),
    )


def create_evidence_item(
    connection: Connection[Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO evidence_items (
            source_id,
            country_id,
            legal_signal_id,
            title,
            summary,
            url,
            quote,
            evidence_type,
            confidence_level,
            claim,
            excerpt,
            retrieved_at,
            confidence,
            status,
            published_at
        )
        VALUES (
            %s::uuid,
            %s::uuid,
            %s::uuid,
            %s,
            %s,
            %s,
            %s,
            'decision_evidence',
            %s,
            %s,
            %s,
            CURRENT_DATE,
            %s,
            %s,
            CURRENT_DATE
        )
        RETURNING {EVIDENCE_RETURNING}
        """,
        (
            payload.get("source_id"),
            payload.get("country_id"),
            payload.get("legal_signal_id"),
            payload.get("claim") or "Draft evidence claim",
            payload.get("excerpt")
            or payload.get("claim")
            or "Draft evidence excerpt",
            payload.get("url"),
            payload.get("excerpt"),
            payload.get("confidence") or "medium",
            payload.get("claim"),
            payload.get("excerpt"),
            payload.get("confidence") or "medium",
            payload.get("status"),
        ),
    )


def patch_evidence_item(
    connection: Connection[Any],
    evidence_item_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    payload = _mirror_evidence_fields(payload)
    return _patch_entity(
        connection,
        "evidence_items",
        evidence_item_id,
        payload,
        EVIDENCE_PATCH_FIELDS
        | {"title", "summary", "quote", "confidence_level"},
        EVIDENCE_RETURNING,
    )


def get_legal_signal_for_admin(
    connection: Connection[Any], signal_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"SELECT {LEGAL_SIGNAL_RETURNING} FROM legal_signals WHERE id::text = %s",
        (signal_id,),
    )


def create_legal_signal(
    connection: Connection[Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    title = (
        payload.get("title_en")
        or payload.get("title_ru")
        or "Draft legal signal"
    )
    summary = (
        payload.get("summary_en")
        or payload.get("summary_ru")
        or "Draft summary"
    )
    return execute_one(
        connection,
        f"""
        INSERT INTO legal_signals (
            country_id,
            source_id,
            title,
            summary,
            title_en,
            title_ru,
            summary_en,
            summary_ru,
            signal_type,
            sentiment,
            severity,
            impact_direction,
            impact_level,
            affected_groups,
            published_date,
            effective_date,
            confidence,
            confidence_level,
            status,
            legal_status,
            published_at
        )
        VALUES (
            %s::uuid,
            %s::uuid,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::jsonb,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING {LEGAL_SIGNAL_RETURNING}
        """,
        (
            payload.get("country_id"),
            payload.get("source_id"),
            title,
            summary,
            payload.get("title_en"),
            payload.get("title_ru"),
            payload.get("summary_en"),
            payload.get("summary_ru"),
            payload.get("signal_type") or "other",
            _sentiment_from_impact(payload.get("impact_direction")),
            payload.get("impact_level") or "low",
            payload.get("impact_direction") or "neutral",
            payload.get("impact_level") or "low",
            json.dumps(payload.get("affected_groups") or []),
            payload.get("published_date"),
            payload.get("effective_date"),
            payload.get("confidence") or "medium",
            payload.get("confidence") or "medium",
            payload.get("status"),
            payload.get("legal_status") or "unknown",
            payload.get("published_date"),
        ),
    )


def patch_legal_signal(
    connection: Connection[Any],
    signal_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    payload = _mirror_legal_signal_fields(payload)
    return _patch_entity(
        connection,
        "legal_signals",
        signal_id,
        payload,
        LEGAL_SIGNAL_PATCH_FIELDS
        | {
            "title",
            "summary",
            "sentiment",
            "severity",
            "confidence_level",
            "published_at",
        },
        LEGAL_SIGNAL_RETURNING,
    )


def get_country_profile_for_admin(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT {COUNTRY_CARD_RETURNING}
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s AND cc.locale = %s
        """,
        (country_slug, locale),
    )


def patch_country_profile(
    connection: Connection[Any],
    country_slug: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    locale = payload.pop("locale", "en")
    existing = fetch_one(
        connection,
        """
        SELECT cc.id::text AS id
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s AND cc.locale = %s
        """,
        (country_slug, locale),
    )
    if existing is None:
        return None
    return _patch_entity(
        connection,
        "country_cards",
        str(existing["id"]),
        payload,
        COUNTRY_CARD_PATCH_FIELDS,
        COUNTRY_CARD_RETURNING,
    )


def get_user_story_for_admin(
    connection: Connection[Any], story_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"SELECT {USER_STORY_RETURNING} FROM user_stories WHERE id::text = %s",
        (story_id,),
    )


def create_user_story_for_admin(
    connection: Connection[Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO user_stories (
            origin_country_id,
            destination_country_id,
            city,
            year,
            scenario,
            budget_initial_usd,
            budget_monthly_usd,
            legal_path,
            documents_used,
            problems,
            positive_outcome,
            negative_outcome,
            advice,
            satisfaction_score,
            verification_status,
            status,
            is_synthetic,
            notes
        )
        VALUES (
            %s::uuid,
            %s::uuid,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::jsonb,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING {USER_STORY_RETURNING}
        """,
        (
            payload.get("origin_country_id"),
            payload.get("destination_country_id"),
            payload.get("city"),
            payload.get("year"),
            payload.get("scenario"),
            payload.get("budget_initial_usd"),
            payload.get("budget_monthly_usd"),
            payload.get("legal_path"),
            json.dumps(payload.get("documents_used") or []),
            payload.get("problems"),
            payload.get("positive_outcome"),
            payload.get("negative_outcome"),
            payload.get("advice"),
            payload.get("satisfaction_score"),
            payload.get("verification_status"),
            payload.get("status"),
            payload.get("is_synthetic"),
            payload.get("notes"),
        ),
    )


def patch_user_story_for_admin(
    connection: Connection[Any],
    story_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    if "documents_used" in payload:
        payload["documents_used"] = json.dumps(payload["documents_used"] or [])
    return _patch_entity(
        connection,
        "user_stories",
        story_id,
        payload,
        USER_STORY_PATCH_FIELDS,
        USER_STORY_RETURNING,
    )


def _patch_entity(
    connection: Connection[Any],
    table: str,
    entity_id: str,
    payload: dict[str, Any],
    allowed_fields: set[str],
    returning: str,
) -> dict[str, Any] | None:
    data = {
        key: value for key, value in payload.items() if key in allowed_fields
    }
    if not data:
        row = connection.execute(
            sql.SQL("SELECT {} FROM {} WHERE id::text = %s").format(
                sql.SQL(returning),
                sql.Identifier(table),
            ),
            (entity_id,),
        ).fetchone()
        return cast(dict[str, Any] | None, row)
    set_parts = [
        sql.SQL("{} = %s").format(sql.Identifier(field)) for field in data
    ]
    values: list[Any] = []
    for field, value in data.items():
        values.append(
            json.dumps(value or []) if field == "affected_groups" else value
        )
    values.append(entity_id)
    query = sql.SQL("""
        UPDATE {}
        SET {}, updated_at = NOW()
        WHERE id::text = %s
        RETURNING {}
    """).format(
        sql.Identifier(table),
        sql.SQL(", ").join(set_parts),
        sql.SQL(returning),
    )
    row = connection.execute(query, tuple(values)).fetchone()
    return cast(dict[str, Any] | None, row)


def _mirror_source_confidence(payload: dict[str, Any]) -> dict[str, Any]:
    if "confidence" in payload:
        payload["reliability_level"] = payload["confidence"]
    return payload


def _mirror_evidence_fields(payload: dict[str, Any]) -> dict[str, Any]:
    if "claim" in payload:
        payload["title"] = payload["claim"] or "Draft evidence claim"
    if "excerpt" in payload:
        payload["summary"] = (
            payload["excerpt"]
            or payload.get("claim")
            or "Draft evidence excerpt"
        )
        payload["quote"] = payload["excerpt"]
    if "confidence" in payload:
        payload["confidence_level"] = payload["confidence"]
    return payload


def _mirror_legal_signal_fields(payload: dict[str, Any]) -> dict[str, Any]:
    if "title_en" in payload or "title_ru" in payload:
        title = payload.get("title_en") or payload.get("title_ru")
        if title:
            payload["title"] = title
    if "summary_en" in payload or "summary_ru" in payload:
        summary = payload.get("summary_en") or payload.get("summary_ru")
        if summary:
            payload["summary"] = summary
    if "impact_direction" in payload:
        payload["sentiment"] = _sentiment_from_impact(
            payload.get("impact_direction")
        )
    if "impact_level" in payload:
        payload["severity"] = payload["impact_level"]
    if "confidence" in payload:
        payload["confidence_level"] = payload["confidence"]
    if "published_date" in payload:
        payload["published_at"] = payload["published_date"]
    return payload


def _sentiment_from_impact(impact_direction: Any) -> str:
    if impact_direction in {"positive", "negative", "neutral", "mixed"}:
        return str(impact_direction)
    return "unknown"
