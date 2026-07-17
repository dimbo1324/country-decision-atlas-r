from __future__ import annotations

from utils.synthetic_data.core.dataset_diff import MetricChange, diff_worlds
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import (
    MetricSnapshot,
    SyntheticCountry,
    SyntheticEvent,
    SyntheticScenario,
    SyntheticSource,
    SyntheticWorld,
    WorldMetadata,
)


def _country(
    *, slug: str, archetype: str, metrics: dict[str, int]
) -> SyntheticCountry:
    country_id = f"country-{slug}"
    event = SyntheticEvent(
        event_id=f"event-{slug}",
        country_id=country_id,
        as_of="2026-01-01",
        metric=next(iter(metrics)),
        direction="improved",
        summary="test event",
    )
    source = SyntheticSource(
        source_id=f"source-{slug}",
        country_id=country_id,
        event_id=event.event_id,
        title="test source",
        url=f"synthetic://test/{slug}",
        confidence=50,
    )
    return SyntheticCountry(
        country_id=country_id,
        code=f"SYN-{slug[:3].upper()}",
        slug=slug,
        name=slug.title(),
        archetype=archetype,
        metric_history=(MetricSnapshot(as_of="2026-01-01", metrics=metrics),),
        strengths=(),
        risks=(),
        uncertainties=(),
        events=(event,),
        sources=(source,),
    )


def _scenario(*, scenario_id: str, category: str) -> SyntheticScenario:
    return SyntheticScenario(
        scenario_id=scenario_id,
        title="test scenario",
        category=category,
        profile="balanced",
        initial_state={},
        steps=(),
        expected_results=(),
        related_artifacts=("country-a",),
        risk_labels=("test",),
    )


def _world(
    *,
    dataset_id: str,
    seed: int,
    profile: str,
    countries: tuple[SyntheticCountry, ...],
    scenarios: tuple[SyntheticScenario, ...] = (),
) -> SyntheticWorld:
    return SyntheticWorld(
        metadata=WorldMetadata(
            dataset_id=dataset_id,
            schema_version="1",
            generator_version="test",
            seed=seed,
            profile=profile,
            supported_locales=("en-US",),
            source_config_checksum="checksum",
            generated_on="2026-01-01",
        ),
        countries=countries,
        scenarios=scenarios,
    )


def test_diff_of_a_world_against_itself_is_identical() -> None:
    world = _world(
        dataset_id="syn-a",
        seed=1,
        profile="balanced",
        countries=(
            _country(slug="alpha", archetype="stable", metrics={"economy": 50}),
        ),
        scenarios=(_scenario(scenario_id="s1", category="comparison"),),
    )

    diff = diff_worlds(world, world)

    assert diff.is_identical
    assert diff.countries_added == ()
    assert diff.countries_removed == ()
    assert diff.countries_changed == ()
    assert diff.scenario_category_diffs == ()
    assert diff.scenario_count_a == diff.scenario_count_b == 1


def test_diff_reports_added_and_removed_countries() -> None:
    world_a = _world(
        dataset_id="syn-a",
        seed=1,
        profile="balanced",
        countries=(
            _country(slug="alpha", archetype="stable", metrics={"economy": 50}),
            _country(slug="beta", archetype="stable", metrics={"economy": 40}),
        ),
    )
    world_b = _world(
        dataset_id="syn-b",
        seed=2,
        profile="balanced",
        countries=(
            _country(slug="alpha", archetype="stable", metrics={"economy": 50}),
            _country(slug="gamma", archetype="stable", metrics={"economy": 60}),
        ),
    )

    diff = diff_worlds(world_a, world_b)

    assert not diff.is_identical
    assert diff.countries_added == ("gamma",)
    assert diff.countries_removed == ("beta",)
    assert diff.countries_changed == ()


def test_diff_reports_metric_and_archetype_changes_for_shared_countries() -> (
    None
):
    world_a = _world(
        dataset_id="syn-a",
        seed=1,
        profile="balanced",
        countries=(
            _country(
                slug="alpha",
                archetype="stable",
                metrics={"economy": 50, "safety": 70},
            ),
        ),
    )
    world_b = _world(
        dataset_id="syn-b",
        seed=1,
        profile="crisis",
        countries=(
            _country(
                slug="alpha",
                archetype="crisis_zone",
                metrics={"economy": 30, "safety": 70},
            ),
        ),
    )

    diff = diff_worlds(world_a, world_b)

    assert not diff.is_identical
    assert len(diff.countries_changed) == 1
    country_diff = diff.countries_changed[0]
    assert country_diff.slug == "alpha"
    assert country_diff.archetype_a == "stable"
    assert country_diff.archetype_b == "crisis_zone"
    assert country_diff.metric_changes == (
        MetricChange(metric="economy", value_a=50, value_b=30),
    )


def test_diff_reports_scenario_category_count_changes() -> None:
    world_a = _world(
        dataset_id="syn-a",
        seed=1,
        profile="balanced",
        countries=(
            _country(slug="alpha", archetype="stable", metrics={"economy": 50}),
        ),
        scenarios=(_scenario(scenario_id="s1", category="comparison"),),
    )
    world_b = _world(
        dataset_id="syn-b",
        seed=1,
        profile="balanced",
        countries=(
            _country(slug="alpha", archetype="stable", metrics={"economy": 50}),
        ),
        scenarios=(
            _scenario(scenario_id="s1", category="comparison"),
            _scenario(scenario_id="s2", category="comparison"),
        ),
    )

    diff = diff_worlds(world_a, world_b)

    assert not diff.is_identical
    assert diff.scenario_count_a == 1
    assert diff.scenario_count_b == 2
    assert len(diff.scenario_category_diffs) == 1
    category_diff = diff.scenario_category_diffs[0]
    assert category_diff.category == "comparison"
    assert category_diff.count_a == 1
    assert category_diff.count_b == 2


def test_diff_of_full_generated_worlds_with_different_seeds_is_disjoint() -> (
    None
):
    input_data = load_world_input()
    world_a = WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=1, profile="balanced")
    )
    world_b = WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=2, profile="balanced")
    )

    diff = diff_worlds(world_a, world_b)

    slugs_a = {country.slug for country in world_a.countries}
    slugs_b = {country.slug for country in world_b.countries}
    assert set(diff.countries_added) == slugs_b - slugs_a
    assert set(diff.countries_removed) == slugs_a - slugs_b
