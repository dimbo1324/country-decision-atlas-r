from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "database"
    / "fixtures"
    / "demo_countries"
)
DEMO_SLUGS = ("russia", "uruguay", "argentina")


@dataclass(frozen=True)
class TableSpec:
    name: str
    select_sql: str
    conflict_columns: tuple[str, ...]


@dataclass(frozen=True)
class LookupSpec:
    """A reference table the demo fixtures point to but don't own.

    `locales`, `scenarios`, and `cii_metric_definitions` all assign their id
    via `gen_random_uuid()` with no fixed seed, so a fixture exported from one
    database instance embeds ids (`locale_id`, `scenario_id`, `metric_id`)
    that a different fresh instance will never reproduce. `natural_key` is
    the stable column restore can use to find the current row instead.
    """

    table: str
    natural_key: str


EXTERNAL_LOOKUPS: tuple[LookupSpec, ...] = (
    LookupSpec("locales", "code"),
    LookupSpec("scenarios", "slug"),
    LookupSpec("cii_metric_definitions", "slug"),
)


TABLE_SPECS: tuple[TableSpec, ...] = (
    TableSpec(
        "countries",
        "SELECT * FROM countries WHERE slug = ANY(%(slugs)s)",
        ("id",),
    ),
    TableSpec(
        "translations",
        """
        SELECT t.* FROM translations t
        JOIN countries c ON c.id = t.entity_id
        WHERE t.entity_type = 'country' AND c.slug = ANY(%(slugs)s)
        """,
        ("entity_type", "entity_id", "field_name", "locale_id"),
    ),
    TableSpec(
        "country_profiles",
        """
        SELECT cp.* FROM country_profiles cp
        JOIN countries c ON c.id = cp.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_cards",
        """
        SELECT cc.* FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "sources",
        """
        SELECT s.* FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "evidence_items",
        """
        SELECT ei.* FROM evidence_items ei
        JOIN countries c ON c.id = ei.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "legal_signals",
        """
        SELECT ls.* FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "legal_signal_events",
        """
        SELECT lse.* FROM legal_signal_events lse
        JOIN countries c ON c.id = lse.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_metric_values",
        """
        SELECT cmv.* FROM country_metric_values cmv
        JOIN countries c ON c.id = cmv.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_cii_scores",
        """
        SELECT ccs.* FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_scores",
        """
        SELECT cs.* FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_score_breakdowns",
        """
        SELECT csb.* FROM country_score_breakdowns csb
        JOIN country_scores cs ON cs.id = csb.country_score_id
        JOIN countries c ON c.id = cs.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "routes",
        """
        SELECT r.* FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "route_documents",
        """
        SELECT rd.* FROM route_documents rd
        JOIN routes r ON r.id = rd.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "route_sources",
        """
        SELECT rs.* FROM route_sources rs
        JOIN routes r ON r.id = rs.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("route_id", "source_id"),
    ),
    TableSpec(
        "route_evidence",
        """
        SELECT re.* FROM route_evidence re
        JOIN routes r ON r.id = re.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("route_id", "evidence_item_id"),
    ),
    TableSpec(
        "route_checklist_items",
        """
        SELECT rci.* FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_pair_compatibility",
        """
        SELECT cpc.* FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE oc.slug = ANY(%(slugs)s) AND dc.slug = ANY(%(slugs)s)
        """,
        ("id",),
    ),
    TableSpec(
        "country_pair_compatibility_sources",
        """
        SELECT cps.* FROM country_pair_compatibility_sources cps
        JOIN country_pair_compatibility cpc ON cpc.id = cps.country_pair_id
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE oc.slug = ANY(%(slugs)s) AND dc.slug = ANY(%(slugs)s)
        """,
        ("country_pair_id", "source_id"),
    ),
    TableSpec(
        "country_pair_compatibility_evidence",
        """
        SELECT cpe.* FROM country_pair_compatibility_evidence cpe
        JOIN country_pair_compatibility cpc ON cpc.id = cpe.country_pair_id
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE oc.slug = ANY(%(slugs)s) AND dc.slug = ANY(%(slugs)s)
        """,
        ("country_pair_id", "evidence_item_id"),
    ),
)
