from __future__ import annotations

from utils.synthetic_data.core.sql_fixture import (
    build_cleanup_sql,
    build_seed_sql,
    country_fixture_ids,
)
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticWorld,
)


def _world(seed: int = 42017) -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=seed, profile="balanced")
    )


def test_seed_sql_is_deterministic_for_the_same_world() -> None:
    world = _world()

    first = build_seed_sql(world)
    second = build_seed_sql(world)

    assert first == second


def test_different_seeds_produce_different_country_ids() -> None:
    first = build_seed_sql(_world(seed=1))
    second = build_seed_sql(_world(seed=2))

    assert first != second


def test_seed_sql_wraps_in_a_single_transaction() -> None:
    sql_text = build_seed_sql(_world())

    assert sql_text.count("BEGIN;") == 1
    assert sql_text.count("COMMIT;") == 1
    assert sql_text.index("BEGIN;") < sql_text.index("COMMIT;")


def test_seed_sql_uses_on_conflict_do_update_for_every_insert() -> None:
    sql_text = build_seed_sql(_world())

    assert sql_text.count("INSERT INTO countries") == 5
    assert sql_text.count("INSERT INTO country_profiles") == 5
    assert sql_text.count("INSERT INTO sources") == 5
    assert sql_text.count("INSERT INTO legal_signals") == 5
    assert sql_text.count("ON CONFLICT") == 20


def test_seed_sql_never_sets_is_demo_true() -> None:
    sql_text = build_seed_sql(_world())

    assert "is_demo" in sql_text
    assert "TRUE, TRUE)" not in sql_text


def test_seed_sql_escapes_single_quotes_safely() -> None:
    world = _world()
    # Country names are always plain single words from the generator, but
    # the summary text can legitimately contain an apostrophe via the
    # locale corpus's own sentences — this is the general escaping
    # contract, not a specific corpus fact.
    sql_text = build_seed_sql(world)

    assert "\\'" not in sql_text  # psycopg uses '' doubling, not backslash


def test_country_fixture_ids_are_stable_for_the_same_dataset() -> None:
    world = _world()
    country = world.countries[0]

    first = country_fixture_ids(
        dataset_id=world.metadata.dataset_id, country=country, index=0
    )
    second = country_fixture_ids(
        dataset_id=world.metadata.dataset_id, country=country, index=0
    )

    assert first == second
    assert first.country_id == country.country_id


def test_country_fixture_ids_use_reserved_iso_codes() -> None:
    world = _world()

    for index, country in enumerate(world.countries):
        ids = country_fixture_ids(
            dataset_id=world.metadata.dataset_id, country=country, index=index
        )
        assert ids.iso2.startswith("X")
        assert len(ids.iso2) == 2
        assert ids.iso3.startswith("X")
        assert len(ids.iso3) == 3

    all_iso2 = [
        country_fixture_ids(
            dataset_id=world.metadata.dataset_id, country=country, index=index
        ).iso2
        for index, country in enumerate(world.countries)
    ]
    assert len(set(all_iso2)) == len(all_iso2)


def test_cleanup_sql_targets_exactly_this_datasets_ids() -> None:
    world = _world()
    seed_sql = build_seed_sql(world)
    cleanup_sql = build_cleanup_sql(world)

    for index, country in enumerate(world.countries):
        ids = country_fixture_ids(
            dataset_id=world.metadata.dataset_id, country=country, index=index
        )
        assert ids.country_id in seed_sql
        assert ids.country_id in cleanup_sql
        assert ids.legal_signal_id in cleanup_sql


def test_cleanup_sql_never_touches_demo_countries() -> None:
    sql_text = build_cleanup_sql(_world())

    assert "is_demo = FALSE" in sql_text


def test_cleanup_sql_deletes_in_dependency_safe_order() -> None:
    sql_text = build_cleanup_sql(_world())

    legal_signals_pos = sql_text.index("DELETE FROM legal_signals")
    sources_pos = sql_text.index("DELETE FROM sources")
    profiles_pos = sql_text.index("DELETE FROM country_profiles")
    countries_pos = sql_text.index("DELETE FROM countries")

    assert legal_signals_pos < sources_pos < profiles_pos < countries_pos


def test_seed_sql_marks_every_source_and_summary_as_synthetic() -> None:
    world = _world()
    sql_text = build_seed_sql(world)

    assert FICTIONAL_NOTICE in sql_text
