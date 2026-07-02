from app.repositories import country_pairs as country_pairs_repository
from app.schemas.country_pairs import CountryPairCompatibilitySummary
from app.schemas.decision_engine import OriginContextStatus
from app.services import country_pairs as country_pairs_service
from psycopg import Connection
from typing import Any


def build_country_pair_contexts(
    connection: Connection[Any],
    origin_slug: str,
    candidate_slugs: list[str],
) -> dict[str, CountryPairCompatibilitySummary]:
    rows = country_pairs_repository.list_destination_compatibility(
        connection, origin_slug
    )
    candidates = set(candidate_slugs)
    contexts: dict[str, CountryPairCompatibilitySummary] = {}
    for row in rows:
        destination_slug = str(row["destination_slug"])
        if destination_slug not in candidates:
            continue
        sources = country_pairs_repository.list_pair_sources(connection, row["id"])
        enriched = {**row, "source_ids": [item["id"] for item in sources]}
        contexts[destination_slug] = country_pairs_service.build_country_pair_summary(
            enriched
        )
    return contexts


def resolve_origin_context_status(
    origin_slug: str | None,
    candidate_slugs: list[str],
    pair_contexts: dict[str, CountryPairCompatibilitySummary],
) -> OriginContextStatus:
    if origin_slug is None:
        return "not_requested"
    if not candidate_slugs:
        return "not_available"
    matched = sum(1 for slug in candidate_slugs if slug in pair_contexts)
    if matched == 0:
        return "not_available"
    if matched == len(candidate_slugs):
        return "available"
    return "partial"
