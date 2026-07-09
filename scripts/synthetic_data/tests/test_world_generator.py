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
