from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from utils.synthetic_data.core.sql_fixture import (
    SYNTHETIC_USER_PASSWORD,
    SYNTHETIC_USER_ROLE,
    build_cleanup_sql,
    build_seed_sql,
    country_fixture_ids,
    user_fixture_ids,
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


_ROOT_DIR = Path(__file__).resolve().parents[3]
_API_DIR = _ROOT_DIR / "apps" / "api"
for _path in (_ROOT_DIR, _API_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from app.services.auth import verify_password  # noqa: E402


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
    world = _world()
    sql_text = build_seed_sql(world)

    assert sql_text.count("INSERT INTO countries") == 5
    assert sql_text.count("INSERT INTO country_profiles") == 5
    assert sql_text.count("INSERT INTO sources") == 5
    assert sql_text.count("INSERT INTO legal_signals") == 5
    assert sql_text.count("INSERT INTO users") == len(world.users)
    assert sql_text.count("INSERT INTO user_auth_credentials") == len(
        world.users
    )
    expected_on_conflict = 4 * 5 + 2 * len(world.users)
    assert sql_text.count("ON CONFLICT") == expected_on_conflict


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

    all_iso3 = [
        country_fixture_ids(
            dataset_id=world.metadata.dataset_id, country=country, index=index
        ).iso3
        for index, country in enumerate(world.countries)
    ]
    assert len(set(all_iso3)) == len(all_iso3)


def test_different_datasets_usually_get_different_iso_codes() -> None:
    """Regression test for a real bug found live during Stage 2
    verification: the original implementation derived iso2/iso3 only
    from a country's index, so every dataset's first country got the
    exact same 'XA'/'XAA' -- loading a second dataset without cleaning
    up the first always collided on countries.iso2's UNIQUE constraint.
    Fixed with a per-dataset-seeded permutation (still not a full
    guarantee -- iso2 only has 26 safe combinations total, see README
    "Known limitations" -- but no longer a certainty either)."""
    first_country = _world(seed=1).countries[0]
    first_ids = country_fixture_ids(
        dataset_id=_world(seed=1).metadata.dataset_id,
        country=first_country,
        index=0,
    )

    iso2_values = set()
    iso3_values = set()
    for seed in range(1, 21):
        world = _world(seed=seed)
        ids = country_fixture_ids(
            dataset_id=world.metadata.dataset_id,
            country=world.countries[0],
            index=0,
        )
        iso2_values.add(ids.iso2)
        iso3_values.add(ids.iso3)

    # Old behavior: every one of these would be identical ('XA'/'XAA').
    assert len(iso2_values) > 1
    assert len(iso3_values) > 1
    assert first_ids.iso2 in iso2_values


def test_country_fixture_ids_iso_codes_are_stable_for_the_same_dataset() -> (
    None
):
    world = _world()
    country = world.countries[0]

    first = country_fixture_ids(
        dataset_id=world.metadata.dataset_id, country=country, index=0
    )
    second = country_fixture_ids(
        dataset_id=world.metadata.dataset_id, country=country, index=0
    )

    assert first.iso2 == second.iso2
    assert first.iso3 == second.iso3


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


def test_user_fixture_ids_are_stable_for_the_same_dataset() -> None:
    world = _world()
    user = world.users[0]

    first = user_fixture_ids(dataset_id=world.metadata.dataset_id, user=user)
    second = user_fixture_ids(dataset_id=world.metadata.dataset_id, user=user)

    assert first == second


def test_different_users_get_different_fixture_ids() -> None:
    world = _world()

    ids = [
        user_fixture_ids(dataset_id=world.metadata.dataset_id, user=user)
        for user in world.users
    ]

    assert len({fixture_ids.user_id for fixture_ids in ids}) == len(ids)
    assert len({fixture_ids.credential_id for fixture_ids in ids}) == len(ids)


def test_every_user_gets_the_ordinary_real_role() -> None:
    """Owner decision (Stage 2 spike): SyntheticUser.role ('author'/'user',
    a content-authorship concept) never becomes the real users.role RBAC
    value directly -- every synthetic user gets the safe 'user' default."""
    world = _world()
    sql_text = build_seed_sql(world)

    role_values = set(re.findall(r"', '([a-z]+)', 'active', '\{", sql_text))
    assert role_values == {SYNTHETIC_USER_ROLE}


def test_every_user_password_hash_verifies_against_the_real_app() -> None:
    """The whole point of writing users into the real `users` table: a
    manual tester or e2e test must be able to actually log in. Every
    password_hash in the fixture must verify against the real app's own
    verify_password() using the documented SYNTHETIC_USER_PASSWORD."""
    world = _world()
    sql_text = build_seed_sql(world)

    hashes = re.findall(r"'(pbkdf2_sha256\$[^']+)'", sql_text)
    assert len(hashes) == len(world.users)
    assert all(
        verify_password(SYNTHETIC_USER_PASSWORD, encoded) for encoded in hashes
    )
    assert not any(
        verify_password("definitely-the-wrong-password", encoded)
        for encoded in hashes
    )


def test_user_metadata_marks_every_row_as_synthetic() -> None:
    """Invariant #26 (docs/architecture/invariants.md):
    synthetic content is always marked."""
    world = _world()
    sql_text = build_seed_sql(world)

    metadata_blobs = re.findall(r'\{"synthetic":[^}]+\}', sql_text)
    assert len(metadata_blobs) == len(world.users)
    for blob in metadata_blobs:
        payload = json.loads(blob)
        assert payload["synthetic"] is True
        assert payload["dataset_id"] == world.metadata.dataset_id
        assert payload["notice"] == FICTIONAL_NOTICE


def test_seed_sql_users_use_the_reserved_email_domain() -> None:
    world = _world()
    sql_text = build_seed_sql(world)

    for user in world.users:
        assert user.email.endswith("@example.test")
        assert user.email in sql_text


def test_cleanup_sql_deletes_user_credentials_before_users() -> None:
    sql_text = build_cleanup_sql(_world())

    credentials_pos = sql_text.index("DELETE FROM user_auth_credentials")
    users_pos = sql_text.index("DELETE FROM users")

    assert credentials_pos < users_pos


def test_cleanup_sql_targets_exactly_this_datasets_user_ids() -> None:
    world = _world()
    seed_sql = build_seed_sql(world)
    cleanup_sql = build_cleanup_sql(world)

    for user in world.users:
        ids = user_fixture_ids(dataset_id=world.metadata.dataset_id, user=user)
        assert ids.user_id in seed_sql
        assert ids.user_id in cleanup_sql
        assert ids.credential_id in seed_sql
        assert ids.credential_id in cleanup_sql


def test_cleanup_sql_only_targets_this_datasets_users_not_others() -> None:
    """Cleanup isolation: two different datasets' user fixtures must never
    collide or cross-delete each other's rows."""
    first_world = _world(seed=1)
    second_world = _world(seed=2)

    first_cleanup = build_cleanup_sql(first_world)
    second_user_ids = {
        user_fixture_ids(
            dataset_id=second_world.metadata.dataset_id, user=user
        ).user_id
        for user in second_world.users
    }

    assert not any(user_id in first_cleanup for user_id in second_user_ids)
