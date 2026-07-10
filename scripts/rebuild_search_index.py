from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from psycopg import Connection, connect
from psycopg.rows import dict_row
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "apps" / "api"
for import_path in (ROOT_DIR, API_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from app.core.config import get_settings  # noqa: E402
from app.repositories import search_index, search_sources  # noqa: E402
from app.services import search_index as search_index_service  # noqa: E402


_content_hash = search_index_service.content_hash


LOCALES = ("en", "ru")


def _upsert(
    connection: Connection[Any],
    summary: dict[str, int],
    dry_run: bool,
    *,
    entity_type: str,
    entity_id: str,
    country_slug: str | None,
    locale: str,
    title: str,
    body_summary: str,
    path: str,
    source_updated_at: Any,
) -> None:
    if not title.strip() or not path.strip():
        summary["skipped_invalid"] += 1
        return
    content_hash = _content_hash(
        entity_type, entity_id, locale, title, body_summary
    )
    if not dry_run:
        search_index.upsert_search_document(
            connection,
            entity_type=entity_type,
            entity_id=entity_id,
            country_slug=country_slug,
            locale=locale,
            title=title,
            summary=body_summary,
            body="",
            path=path,
            status="published",
            content_hash=content_hash,
            source_updated_at=source_updated_at,
        )
    summary["documents_upserted"] += 1


def _index_locale_partitioned(
    connection: Connection[Any],
    rows: list[dict[str, Any]],
    entity_type: str,
    path_fn: Callable[[dict[str, Any]], str],
    dry_run: bool,
    summary: dict[str, int],
    country_filter: str | None,
) -> set[tuple[str, str]]:
    kept: set[tuple[str, str]] = set()
    for row in rows:
        country_slug = row.get("country_slug")
        if country_filter and country_slug != country_filter:
            continue
        locale = str(row["locale"])
        _upsert(
            connection,
            summary,
            dry_run,
            entity_type=entity_type,
            entity_id=row["entity_id"],
            country_slug=country_slug,
            locale=locale,
            title=str(row.get("title") or ""),
            body_summary=str(row.get("summary") or ""),
            path=path_fn(row),
            source_updated_at=row.get("updated_at"),
        )
        kept.add((row["entity_id"], locale))
    return kept


def _index_dual_locale(
    connection: Connection[Any],
    rows: list[dict[str, Any]],
    entity_type: str,
    path_fn: Callable[[dict[str, Any]], str],
    dry_run: bool,
    summary: dict[str, int],
    country_filter: str | None,
) -> set[tuple[str, str]]:
    kept: set[tuple[str, str]] = set()
    for row in rows:
        country_slug = row.get("country_slug")
        if country_filter and country_slug != country_filter:
            continue
        for locale in LOCALES:
            title = str(row.get(f"title_{locale}") or "")
            body_summary = str(row.get(f"summary_{locale}") or "")
            _upsert(
                connection,
                summary,
                dry_run,
                entity_type=entity_type,
                entity_id=row["entity_id"],
                country_slug=country_slug,
                locale=locale,
                title=title,
                body_summary=body_summary,
                path=path_fn(row),
                source_updated_at=row.get("updated_at"),
            )
            kept.add((row["entity_id"], locale))
    return kept


def _index_single_locale_both(
    connection: Connection[Any],
    rows: list[dict[str, Any]],
    entity_type: str,
    path_fn: Callable[[dict[str, Any]], str],
    dry_run: bool,
    summary: dict[str, int],
    country_filter: str | None,
) -> set[tuple[str, str]]:
    kept: set[tuple[str, str]] = set()
    for row in rows:
        country_slug = row.get("country_slug")
        if country_filter and country_slug != country_filter:
            continue
        for locale in LOCALES:
            _upsert(
                connection,
                summary,
                dry_run,
                entity_type=entity_type,
                entity_id=row["entity_id"],
                country_slug=country_slug,
                locale=locale,
                title=str(row.get("title") or ""),
                body_summary=str(row.get("summary") or ""),
                path=path_fn(row),
                source_updated_at=row.get("updated_at"),
            )
            kept.add((row["entity_id"], locale))
    return kept


ENTITY_JOBS: dict[str, dict[str, Any]] = {
    "country": {
        "fetch": search_sources.list_indexable_countries,
        "index": _index_locale_partitioned,
        "path": lambda row: f"/countries/{row['path_slug']}",
    },
    "route": {
        "fetch": search_sources.list_indexable_routes,
        "index": _index_dual_locale,
        "path": lambda row: f"/routes/{row['path_id']}",
    },
    "route_checklist_item": {
        "fetch": search_sources.list_indexable_route_checklist_items,
        "index": _index_dual_locale,
        "path": lambda row: f"/routes/{row['path_id']}",
    },
    "legal_signal": {
        "fetch": search_sources.list_indexable_legal_signals,
        "index": _index_dual_locale,
        "path": lambda row: f"/legal-signals?country_slug={row['path_slug']}",
    },
    "source": {
        "fetch": search_sources.list_indexable_sources,
        "index": _index_single_locale_both,
        "path": lambda row: (
            f"/sources?country_slug={row['country_slug']}"
            if row.get("country_slug")
            else "/sources"
        ),
    },
    "evidence_item": {
        "fetch": search_sources.list_indexable_evidence_items,
        "index": _index_single_locale_both,
        "path": lambda row: (
            f"/sources?country_slug={row['country_slug']}"
            if row.get("country_slug")
            else "/sources"
        ),
    },
    "country_pair_compatibility": {
        "fetch": search_sources.list_indexable_country_pairs,
        "index": _index_single_locale_both,
        "path": lambda row: f"/countries/{row['path_slug']}",
    },
    "methodology": {
        "fetch": search_sources.list_indexable_methodology_sections,
        "index": _index_dual_locale,
        "path": lambda _row: "/methodology",
    },
    "glossary_term": {
        "fetch": search_sources.list_indexable_glossary_terms,
        "index": _index_dual_locale,
        "path": lambda _row: "/methodology",
    },
}


def rebuild(
    connection: Connection[Any],
    entity_types: list[str] | None,
    country: str | None,
    dry_run: bool,
) -> dict[str, Any]:
    summary: dict[str, int] = {
        "documents_upserted": 0,
        "documents_deleted": 0,
        "skipped_invalid": 0,
        "entity_types_processed": 0,
    }
    targets = entity_types or list(ENTITY_JOBS.keys())
    errors: list[str] = []
    for entity_type in targets:
        job = ENTITY_JOBS.get(entity_type)
        if job is None:
            errors.append(f"unknown_entity_type:{entity_type}")
            continue
        try:
            rows = job["fetch"](connection)
            kept = job["index"](
                connection,
                rows,
                entity_type,
                job["path"],
                dry_run,
                summary,
                country,
            )
            if not country and not dry_run:
                existing = search_index.list_indexed_entity_ids(
                    connection, entity_type
                )
                stale = [
                    (str(item["entity_id"]), str(item["locale"]))
                    for item in existing
                    if (str(item["entity_id"]), str(item["locale"])) not in kept
                ]
                summary["documents_deleted"] += (
                    search_index.delete_search_documents_by_ids(
                        connection, entity_type, stale
                    )
                )
            summary["entity_types_processed"] += 1
        except Exception as error:
            errors.append(f"{entity_type}:{error}")
    return {
        "ok": len(errors) == 0,
        "dry_run": dry_run,
        "summary": summary,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild the public search index."
    )
    parser.add_argument("--all", action="store_true", default=False)
    parser.add_argument("--entity-type", action="append", default=None)
    parser.add_argument("--country", default=None)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args(argv)

    entity_types = args.entity_type if args.entity_type else None
    if entity_types:
        unknown = [item for item in entity_types if item not in ENTITY_JOBS]
        if unknown:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "errors": [f"unknown_entity_type:{u}" for u in unknown],
                    }
                )
            )
            return 1

    settings = get_settings()
    with connect(settings.database_url, row_factory=dict_row) as connection:
        result = rebuild(connection, entity_types, args.country, args.dry_run)
        if not args.dry_run:
            connection.commit()

    print(json.dumps(result, default=str))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
