from __future__ import annotations

from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import WorldInput, load_world_input
from scripts.synthetic_data.core.world_models import SyntheticWorld
from scripts.synthetic_data.core.world_validation import validate_world


def _world() -> tuple[SyntheticWorld, WorldInput]:
    input_data = load_world_input()
    return (
        WorldGenerator(input_data=input_data).generate(
            WorldGenerationOptions(seed=42017, profile="balanced")
        ),
        input_data,
    )


def test_validator_rejects_wrong_country_count() -> None:
    world, input_data = _world()
    invalid_world = world.model_copy(update={"countries": world.countries[:3]})

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("between 4 and 5 countries" in error for error in errors)


def test_validator_rejects_source_for_another_country() -> None:
    world, input_data = _world()
    country = world.countries[0]
    invalid_source = country.sources[0].model_copy(
        update={"country_id": "other-country"}
    )
    invalid_country = country.model_copy(update={"sources": (invalid_source,)})
    invalid_world = world.model_copy(
        update={"countries": (invalid_country, *world.countries[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert f"{country.slug}: source has another country id" in errors


def test_validator_rejects_forbidden_country_name() -> None:
    world, input_data = _world()
    country = world.countries[0]
    forbidden_name = next(iter(input_data.forbidden_country_names))
    renamed_country = country.model_copy(update={"name": forbidden_name})
    invalid_world = world.model_copy(
        update={"countries": (renamed_country, *world.countries[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("country name is forbidden" in error for error in errors)


def test_validator_rejects_unexplained_metric_change() -> None:
    world, input_data = _world()
    country = world.countries[0]
    # Drop the only event, which was the sole explanation for the metric
    # change baked into the country's synthetic history.
    orphaned_country = country.model_copy(update={"events": ()})
    invalid_world = world.model_copy(
        update={"countries": (orphaned_country, *world.countries[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("unexplained" in error for error in errors)


def test_validator_rejects_metric_change_pointing_to_wrong_event_metric() -> (
    None
):
    world, input_data = _world()
    country = world.countries[0]
    original_event = country.events[0]
    other_metric = next(
        metric
        for metric in country.current_metrics
        if metric != original_event.metric
    )
    mismatched_event = original_event.model_copy(
        update={"metric": other_metric}
    )
    invalid_country = country.model_copy(update={"events": (mismatched_event,)})
    invalid_world = world.model_copy(
        update={"countries": (invalid_country, *world.countries[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("unexplained" in error for error in errors)
