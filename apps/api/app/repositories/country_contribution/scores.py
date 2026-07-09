import json
from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def get_scenario_id_by_slug(
    connection: Connection[Any], slug: str
) -> str | None:
    row = fetch_one(
        connection,
        "SELECT id::text AS id FROM scenarios WHERE slug = %s AND is_active = TRUE",
        (slug,),
    )
    return str(row["id"]) if row else None


def upsert_country_score(
    connection: Connection[Any],
    *,
    country_id: str,
    scenario_id: str,
    score: float,
    score_label: str,
    confidence: str,
    explanation_en: str,
    explanation_ru: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO country_scores (
            country_id, scenario_id, score, score_label,
            confidence, explanation_en, explanation_ru, calculated_at
        )
        VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (country_id, scenario_id) DO UPDATE
        SET score = EXCLUDED.score,
            score_label = EXCLUDED.score_label,
            confidence = EXCLUDED.confidence,
            explanation_en = EXCLUDED.explanation_en,
            explanation_ru = EXCLUDED.explanation_ru,
            calculated_at = NOW()
        RETURNING id, country_id, scenario_id, score, score_label, confidence,
                  explanation_en, explanation_ru, calculated_at
        """,
        (
            country_id,
            scenario_id,
            score,
            score_label,
            confidence,
            explanation_en,
            explanation_ru,
        ),
    )


def replace_breakdowns(
    connection: Connection[Any],
    *,
    country_score_id: str,
    breakdowns: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    connection.execute(
        "DELETE FROM country_score_breakdowns WHERE country_score_id = %s::uuid",
        (country_score_id,),
    )
    return fetch_all(
        connection,
        """
        INSERT INTO country_score_breakdowns (
            country_score_id, criterion, score, weight, weighted_score,
            explanation_en, explanation_ru, source_ids, confidence
        )
        SELECT
            %s::uuid,
            entry.criterion,
            entry.score,
            entry.weight,
            entry.score * entry.weight,
            entry.explanation_en,
            entry.explanation_ru,
            entry.source_ids::jsonb,
            entry.confidence
        FROM jsonb_to_recordset(%s::jsonb) AS entry(
            criterion TEXT,
            score NUMERIC,
            weight NUMERIC,
            explanation_en TEXT,
            explanation_ru TEXT,
            source_ids JSONB,
            confidence TEXT
        )
        RETURNING id, country_score_id, criterion, score, weight, weighted_score,
                  explanation_en, explanation_ru, source_ids, confidence
        """,
        (country_score_id, _entries_json(breakdowns)),
    )


def _entries_json(breakdowns: list[dict[str, Any]]) -> str:
    return json.dumps(breakdowns, default=str)


def get_country_score(
    connection: Connection[Any], *, country_id: str, scenario_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT id, country_id, scenario_id, score, score_label, confidence,
               explanation_en, explanation_ru, calculated_at
        FROM country_scores
        WHERE country_id = %s::uuid AND scenario_id = %s::uuid
        """,
        (country_id, scenario_id),
    )
