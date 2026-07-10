from __future__ import annotations

from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import load_world_input
from scripts.synthetic_data.core.world_models import SyntheticWorld
from typing import Any, cast


def _generate_world(
    seed: int = 42017,
    country_count: int | None = None,
    generated_on: str | None = "2026-01-01",
) -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(
            seed=seed,
            profile="balanced",
            country_count=country_count,
            generated_on=generated_on,
        )
    )


def test_same_seed_creates_the_same_logical_world() -> None:
    first = _generate_world()
    second = _generate_world()

    assert first.to_dict() == second.to_dict()


def test_same_seed_is_reproducible_regardless_of_calendar_day() -> None:
    """The `generated_on` field is operational metadata, not logical data:
    fixing it explicitly (rather than relying on same-day test execution)
    is what the spec means by 'excluding technical generation time'."""
    first = _generate_world(generated_on="2026-01-01")
    second = _generate_world(generated_on="2030-12-31")

    first_payload = cast(dict[str, Any], first.to_dict())
    second_payload = cast(dict[str, Any], second.to_dict())
    first_metadata = cast(dict[str, Any], first_payload["metadata"])
    second_metadata = cast(dict[str, Any], second_payload["metadata"])
    assert first_metadata["generated_on"] != second_metadata["generated_on"]
    del first_metadata["generated_on"]
    del second_metadata["generated_on"]
    assert first_payload == second_payload


def test_different_seed_changes_the_world() -> None:
    first = _generate_world(seed=42017)
    second = _generate_world(seed=42018)

    assert first.metadata.dataset_id != second.metadata.dataset_id
    assert [country.name for country in first.countries] != [
        country.name for country in second.countries
    ]


def test_generated_world_contains_linked_country_history_events_and_sources() -> (
    None
):
    world = _generate_world()
    forbidden_names = {
        name.casefold() for name in load_world_input().forbidden_country_names
    }

    assert len(world.countries) == 5
    assert len({country.code for country in world.countries}) == 5
    for country in world.countries:
        assert country.name.casefold() not in forbidden_names
        assert country.code.startswith("SYN-")
        assert len(country.metric_history) == 3
        assert country.strengths
        assert country.risks
        assert len(country.events) == 1
        assert len(country.sources) == 1
        assert country.events[0].country_id == country.country_id
        assert country.sources[0].event_id == country.events[0].event_id
        assert country.sources[0].url.startswith("synthetic://")
        assert not all(
            value >= 70 for value in country.current_metrics.values()
        )


def test_country_count_can_be_reduced_to_four() -> None:
    world = _generate_world(country_count=4)

    assert len(world.countries) == 4


def test_every_country_has_an_author_article_and_legal_signal() -> None:
    world = _generate_world()
    country_ids = {country.country_id for country in world.countries}

    assert len(world.authors) == len(world.countries)
    assert len(world.articles) == len(world.countries)
    assert len(world.legal_signals) == len(world.countries)
    assert {author.author_id for author in world.authors} == {
        article.author_id for article in world.articles
    }
    assert {article.country_id for article in world.articles} == country_ids
    assert {signal.country_id for signal in world.legal_signals} == (
        country_ids
    )


def test_legal_signal_reuses_the_countrys_own_event_and_source() -> None:
    world = _generate_world()
    events_by_country = {
        country.country_id: {event.event_id for event in country.events}
        for country in world.countries
    }
    sources_by_country = {
        country.country_id: {source.source_id for source in country.sources}
        for country in world.countries
    }

    for signal in world.legal_signals:
        assert signal.event_id in events_by_country[signal.country_id]
        assert signal.source_id in sources_by_country[signal.country_id]
        assert signal.country_id in signal.affected_country_ids


def test_users_use_reserved_email_domain() -> None:
    world = _generate_world()

    assert world.users
    for user in world.users:
        assert user.email.endswith("@example.test")


def test_comments_cover_multiple_moderation_statuses() -> None:
    world = _generate_world()

    statuses = {comment.moderation_status for comment in world.comments}
    assert len(statuses) >= 2


def test_document_recipes_are_generated_per_country() -> None:
    world = _generate_world()

    assert len(world.document_recipes) == len(world.countries) * len(
        load_world_input().document_recipes
    )
    for recipe in world.document_recipes:
        assert recipe.blocks
        for block in recipe.blocks:
            assert block.text.strip()


def test_scenarios_include_the_four_base_categories() -> None:
    world = _generate_world()

    categories = {scenario.category for scenario in world.scenarios}
    assert categories == {
        "comparison",
        "source_review",
        "change_notification",
        "data_quality",
    }


def test_data_quality_scenario_targets_the_weakest_data_confidence_country() -> (
    None
):
    world = _generate_world()
    weakest = min(
        world.countries,
        key=lambda country: country.current_metrics["data_confidence"],
    )

    data_quality_scenario = next(
        scenario
        for scenario in world.scenarios
        if scenario.category == "data_quality"
    )
    assert weakest.country_id in data_quality_scenario.related_artifacts
