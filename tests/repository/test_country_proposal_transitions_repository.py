"""apps/api/app/repositories/country_contribution/proposals.py against a
real Postgres instance (P2-7, Аудит-эпизод 8): the country-proposal
publication-transition path.

apply_status_transition's WHERE id = %s AND status = %s is an optimistic-
concurrency guard - a mocked connection always "succeeds", so it can't catch
a regression where two concurrent transitions both believe they won. The
published_at CASE WHEN is the same kind of real-SQL behavior.
"""

import psycopg
from app.repositories import auth as auth_repo
from app.repositories.country_contribution import proposals as proposals_repo
from typing import Any


def _make_user(connection: psycopg.Connection[Any], suffix: str) -> str:
    user = auth_repo.create_user(
        connection,
        email=f"repo-proposal-{suffix}@example.local",
        display_name=f"Repo Proposal {suffix}",
        role="user",
    )
    return str(user["id"])


def _make_proposal(
    connection: psycopg.Connection[Any], suffix: str
) -> tuple[str, str]:
    proposer_id = _make_user(connection, suffix)
    country = proposals_repo.create_country_shell(
        connection,
        slug=f"repo-test-{suffix}",
        iso2=suffix[:2].upper(),
        iso3=suffix[:3].upper(),
        name_en=f"Repo Test {suffix}",
    )
    proposal = proposals_repo.create_proposal_row(
        connection,
        proposer_user_id=proposer_id,
        country_id=str(country["id"]),
        slug=f"repo-test-{suffix}",
        name_en=f"Repo Test {suffix}",
        name_ru=f"Репо Тест {suffix}",
        iso2=suffix[:2].upper(),
        iso3=suffix[:3].upper(),
        justification="Integration test justification.",
    )
    return str(proposal["id"]), proposer_id


def test_create_proposal_row_starts_in_draft_status(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)

    row = proposals_repo.get_proposal_by_id(connection, proposal_id)

    assert row is not None
    assert row["status"] == "draft"
    assert row["published_at"] is None


def test_apply_status_transition_updates_status_when_old_status_matches(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)

    result = proposals_repo.apply_status_transition(
        connection,
        proposal_id,
        old_status="draft",
        new_status="review",
    )

    assert result is not None
    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    assert row["status"] == "review"


def test_apply_status_transition_is_noop_when_old_status_does_not_match(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)

    result = proposals_repo.apply_status_transition(
        connection,
        proposal_id,
        old_status="published",
        new_status="archived",
    )

    assert result is None
    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    assert row["status"] == "draft"


def test_apply_status_transition_sets_published_at_when_flag_true(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)
    proposals_repo.apply_status_transition(
        connection, proposal_id, old_status="draft", new_status="review"
    )

    proposals_repo.apply_status_transition(
        connection,
        proposal_id,
        old_status="review",
        new_status="published",
        set_published_at=True,
    )

    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    assert row["status"] == "published"
    assert row["published_at"] is not None


def test_apply_status_transition_leaves_published_at_null_when_flag_false(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)

    proposals_repo.apply_status_transition(
        connection,
        proposal_id,
        old_status="draft",
        new_status="review",
        set_published_at=False,
    )

    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    assert row["published_at"] is None


def test_apply_status_transition_records_moderated_by_and_reason(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)
    moderator_id = _make_user(connection, f"{unique_suffix}-mod")

    proposals_repo.apply_status_transition(
        connection,
        proposal_id,
        old_status="draft",
        new_status="rejected",
        moderated_by=moderator_id,
        moderation_reason="Insufficient sourcing.",
    )

    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    assert row["status"] == "rejected"
    assert str(row["moderated_by"]) == moderator_id
    assert row["moderated_at"] is not None
    assert row["moderation_reason"] == "Insufficient sourcing."


def test_country_slug_exists(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    assert not proposals_repo.country_slug_exists(
        connection, f"repo-test-{unique_suffix}"
    )
    _make_proposal(connection, unique_suffix)
    assert proposals_repo.country_slug_exists(
        connection, f"repo-test-{unique_suffix}"
    )


def test_country_iso_exists_checks_both_iso2_and_iso3(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    iso2 = unique_suffix[:2].upper()
    iso3 = unique_suffix[:3].upper()
    assert not proposals_repo.country_iso_exists(connection, iso2, iso3)

    _make_proposal(connection, unique_suffix)

    assert proposals_repo.country_iso_exists(connection, iso2, "ZZZ")
    assert proposals_repo.country_iso_exists(connection, "ZZ", iso3)


def test_assign_curator_only_succeeds_when_unassigned(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)
    curator_a = _make_user(connection, f"{unique_suffix}-curator-a")
    curator_b = _make_user(connection, f"{unique_suffix}-curator-b")

    first = proposals_repo.assign_curator(
        connection, proposal_id=proposal_id, curator_user_id=curator_a
    )
    second = proposals_repo.assign_curator(
        connection, proposal_id=proposal_id, curator_user_id=curator_b
    )

    assert first is not None
    assert second is None
    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    assert str(row["curator_user_id"]) == curator_a


def test_set_country_active_updates_flag(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    proposal_id, _ = _make_proposal(connection, unique_suffix)
    row = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert row is not None
    country_id = str(row["country_id"])
    assert row["country_is_active"] is False

    proposals_repo.set_country_active(
        connection, country_id=country_id, is_active=True
    )

    updated = proposals_repo.get_proposal_by_id(connection, proposal_id)
    assert updated is not None
    assert updated["country_is_active"] is True
