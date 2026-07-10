from __future__ import annotations

from scripts.synthetic_data.core.content_generator import CountryContent
from scripts.synthetic_data.core.scenario_generator import generate_scenarios
from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import load_world_input
from scripts.synthetic_data.core.world_models import SyntheticWorld


def _generated_world() -> SyntheticWorld:
    input_data = load_world_input()
    return WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )


def _content_by_country(
    world: SyntheticWorld,
) -> dict[str, CountryContent]:
    # Reuses the world's own generated content, keyed the same way the
    # generator keys it internally, so tests exercise realistic input.
    by_country: dict[str, CountryContent] = {}
    for country in world.countries:
        author = next(
            a for a in world.authors if a.author_id == f"author-{country.slug}"
        )
        article = next(
            a
            for a in world.articles
            if a.article_id == f"article-{country.slug}"
        )
        comments = tuple(
            c for c in world.comments if c.article_id == article.article_id
        )
        legal_signal = next(
            s
            for s in world.legal_signals
            if s.signal_id == f"legal-{country.slug}"
        )
        users = tuple(
            u
            for u in world.users
            if u.user_id.startswith(f"user-{country.slug}")
        )
        by_country[country.slug] = CountryContent(
            users=users,
            author=author,
            article=article,
            comments=comments,
            legal_signal=legal_signal,
        )
    return by_country


def test_generate_scenarios_returns_at_least_three_scenarios() -> None:
    world = _generated_world()
    content_by_country = _content_by_country(world)

    scenarios = generate_scenarios(
        profile="balanced",
        countries=world.countries,
        content_by_country=content_by_country,
    )

    assert len(scenarios) >= 3


def test_comparison_scenario_references_two_distinct_countries() -> None:
    world = _generated_world()
    content_by_country = _content_by_country(world)

    scenarios = generate_scenarios(
        profile="balanced",
        countries=world.countries,
        content_by_country=content_by_country,
    )
    comparison = next(s for s in scenarios if s.category == "comparison")

    assert len(comparison.related_artifacts) == 2
    assert comparison.related_artifacts[0] != comparison.related_artifacts[1]
    assert len(comparison.steps) >= 2


def test_source_review_scenario_references_a_moderated_comment() -> None:
    world = _generated_world()
    content_by_country = _content_by_country(world)

    scenarios = generate_scenarios(
        profile="balanced",
        countries=world.countries,
        content_by_country=content_by_country,
    )
    source_review = next(s for s in scenarios if s.category == "source_review")

    comment_id = (
        content_by_country[world.countries[0].slug].comments[0].comment_id
    )
    assert comment_id in source_review.related_artifacts


def test_change_notification_scenario_references_the_countrys_event() -> None:
    world = _generated_world()
    content_by_country = _content_by_country(world)

    scenarios = generate_scenarios(
        profile="balanced",
        countries=world.countries,
        content_by_country=content_by_country,
    )
    change_scenario = next(
        s for s in scenarios if s.category == "change_notification"
    )

    event_id = world.countries[0].events[0].event_id
    assert event_id in change_scenario.related_artifacts
    assert any(
        step.action == "add_to_watchlist" for step in change_scenario.steps
    )
    assert any(
        step.action == "trigger_notification" for step in change_scenario.steps
    )


def test_data_quality_scenario_picks_lowest_confidence_country() -> None:
    world = _generated_world()
    content_by_country = _content_by_country(world)

    scenarios = generate_scenarios(
        profile="balanced",
        countries=world.countries,
        content_by_country=content_by_country,
    )
    data_quality = next(s for s in scenarios if s.category == "data_quality")

    weakest = min(
        world.countries,
        key=lambda country: country.current_metrics["data_confidence"],
    )
    assert weakest.country_id in data_quality.related_artifacts


def test_all_scenarios_have_steps_and_expected_results() -> None:
    world = _generated_world()
    content_by_country = _content_by_country(world)

    scenarios = generate_scenarios(
        profile="balanced",
        countries=world.countries,
        content_by_country=content_by_country,
    )

    for scenario in scenarios:
        assert scenario.steps
        assert scenario.expected_results
        assert scenario.related_artifacts
        assert scenario.risk_labels
