from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


def list_indexable_countries(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cc.country_id::text AS entity_id,
            c.slug AS country_slug,
            cc.locale,
            c.name AS title,
            cc.executive_summary AS summary,
            CONCAT_WS(
                ' ',
                cc.migration_overview,
                cc.tax_overview,
                cc.cost_of_living_overview,
                cc.business_overview,
                cc.safety_overview
            ) AS body,
            c.slug AS path_slug,
            cc.updated_at
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE cc.status = 'published'
          AND c.is_active = TRUE
        """,
    )


def list_indexable_routes(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            r.id::text AS entity_id,
            c.slug AS country_slug,
            r.title AS title_en,
            COALESCE(r.title_ru, r.title) AS title_ru,
            r.summary AS summary_en,
            COALESCE(r.summary_ru, r.summary) AS summary_ru,
            COALESCE(r.eligibility_summary, '') AS body_en,
            COALESCE(r.eligibility_summary_ru, r.eligibility_summary, '') AS body_ru,
            r.id::text AS path_id,
            r.updated_at
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.status = 'published'
        """,
    )


def list_indexable_route_checklist_items(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            rci.id::text AS entity_id,
            c.slug AS country_slug,
            rci.title AS title_en,
            COALESCE(rci.title_ru, rci.title) AS title_ru,
            COALESCE(rci.description, '') AS summary_en,
            COALESCE(rci.description_ru, rci.description, '') AS summary_ru,
            r.id::text AS path_id,
            rci.updated_at
        FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE rci.status = 'published'
          AND r.status = 'published'
        """,
    )


def list_indexable_legal_signals(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id::text AS entity_id,
            c.slug AS country_slug,
            COALESCE(ls.title_en, ls.title, '') AS title_en,
            COALESCE(ls.title_ru, ls.title_en, ls.title, '') AS title_ru,
            COALESCE(ls.summary_en, ls.summary, '') AS summary_en,
            COALESCE(ls.summary_ru, ls.summary_en, ls.summary, '') AS summary_ru,
            c.slug AS path_slug,
            ls.updated_at
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE ls.status = 'published'
        """,
    )


def list_indexable_sources(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            s.id::text AS entity_id,
            c.slug AS country_slug,
            s.title AS title,
            COALESCE(s.publisher, '') AS summary,
            s.updated_at
        FROM sources s
        LEFT JOIN countries c ON c.id = s.country_id
        WHERE s.status = 'published'
        """,
    )


def list_indexable_evidence_items(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ei.id::text AS entity_id,
            c.slug AS country_slug,
            ei.title AS title,
            COALESCE(ei.summary, '') AS summary,
            ei.updated_at
        FROM evidence_items ei
        LEFT JOIN countries c ON c.id = ei.country_id
        WHERE ei.status = 'published'
        """,
    )


def list_indexable_country_pairs(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpc.id::text AS entity_id,
            dc.slug AS country_slug,
            CONCAT(oc.name, ' → ', dc.name) AS title,
            COALESCE(cpc.practical_summary, '') AS summary,
            dc.slug AS path_slug,
            cpc.updated_at
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE cpc.status = 'published'
        """,
    )


def list_indexable_methodology_sections(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS entity_id,
            title AS title_en,
            title_ru,
            summary AS summary_en,
            summary_ru,
            updated_at
        FROM methodology_sections
        WHERE status = 'published'
        """,
    )


def list_indexable_glossary_terms(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS entity_id,
            term AS title_en,
            term_ru AS title_ru,
            definition AS summary_en,
            definition_ru AS summary_ru,
            updated_at
        FROM glossary_terms
        WHERE status = 'published'
        """,
    )
