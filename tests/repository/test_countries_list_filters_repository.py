"""apps/api/app/repositories/countries.py: list_countries/count_countries
filter behavior against a real Postgres instance (P2-7, Аудит-эпизод 8).

is_active/is_demo filtering is a WHERE clause a mocked connection always
"honors" - the point of running it for real is to catch a typo or a dropped
AND that would silently leak demo or inactive countries onto a public list.
"""

import psycopg
from app.repositories import countries as countries_repo
from typing import Any


def _insert_country(
    connection: psycopg.Connection[Any],
    *,
    slug: str,
    iso2: str,
    iso3: str,
    is_active: bool,
    is_demo: bool,
) -> None:
    connection.execute(
        """
        INSERT INTO countries (slug, iso2, iso3, name, is_active, is_demo)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (slug, iso2, iso3, f"Repo List {slug}", is_active, is_demo),
    )


def test_list_countries_excludes_demo_and_inactive(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    visible_slug = f"repo-list-visible-{unique_suffix}"
    demo_slug = f"repo-list-demo-{unique_suffix}"
    inactive_slug = f"repo-list-inactive-{unique_suffix}"
    marker = unique_suffix[0]
    _insert_country(
        connection,
        slug=visible_slug,
        iso2=f"X{marker}".upper(),
        iso3=f"X{marker}0".upper(),
        is_active=True,
        is_demo=False,
    )
    _insert_country(
        connection,
        slug=demo_slug,
        iso2=f"Y{marker}".upper(),
        iso3=f"Y{marker}0".upper(),
        is_active=True,
        is_demo=True,
    )
    _insert_country(
        connection,
        slug=inactive_slug,
        iso2=f"Z{marker}".upper(),
        iso3=f"Z{marker}0".upper(),
        is_active=False,
        is_demo=False,
    )

    rows = countries_repo.list_countries(connection, "en", limit=100, offset=0)
    slugs = {row["slug"] for row in rows}

    assert visible_slug in slugs
    assert demo_slug not in slugs
    assert inactive_slug not in slugs


def test_count_countries_matches_active_non_demo_filter(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    before = countries_repo.count_countries(connection)
    _insert_country(
        connection,
        slug=f"repo-list-count-{unique_suffix}",
        iso2=unique_suffix[:2].upper(),
        iso3=unique_suffix[:3].upper(),
        is_active=True,
        is_demo=False,
    )

    after = countries_repo.count_countries(connection)

    assert after == before + 1


def test_list_active_country_slugs_excludes_demo(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    demo_slug = f"repo-list-slugs-demo-{unique_suffix}"
    _insert_country(
        connection,
        slug=demo_slug,
        iso2=unique_suffix[:2].upper(),
        iso3=unique_suffix[:3].upper(),
        is_active=True,
        is_demo=True,
    )

    slugs = countries_repo.list_active_country_slugs(connection)

    assert demo_slug not in slugs


def test_get_country_excludes_demo_even_when_active(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    demo_slug = f"repo-list-get-demo-{unique_suffix}"
    _insert_country(
        connection,
        slug=demo_slug,
        iso2=unique_suffix[:2].upper(),
        iso3=unique_suffix[:3].upper(),
        is_active=True,
        is_demo=True,
    )

    assert countries_repo.get_country(connection, demo_slug, "en") is None
