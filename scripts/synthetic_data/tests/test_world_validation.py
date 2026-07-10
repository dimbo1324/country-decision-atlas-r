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


def test_validator_rejects_user_with_non_reserved_email() -> None:
    world, input_data = _world()
    bad_user = world.users[0].model_copy(update={"email": "someone@gmail.com"})
    invalid_world = world.model_copy(
        update={"users": (bad_user, *world.users[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("reserved domain" in error for error in errors)


def test_validator_rejects_author_referencing_unknown_user() -> None:
    world, input_data = _world()
    bad_author = world.authors[0].model_copy(update={"user_id": "user-ghost"})
    invalid_world = world.model_copy(
        update={"authors": (bad_author, *world.authors[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("existing user" in error for error in errors)


def test_validator_rejects_article_with_source_from_another_country() -> None:
    world, input_data = _world()
    other_country_source_id = world.countries[1].sources[0].source_id
    bad_article = world.articles[0].model_copy(
        update={"source_ids": (other_country_source_id,)}
    )
    invalid_world = world.model_copy(
        update={"articles": (bad_article, *world.articles[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any(
        "does not belong to the article's country" in error for error in errors
    )


def test_validator_rejects_comment_with_unknown_moderation_status() -> None:
    world, input_data = _world()
    bad_comment = world.comments[0].model_copy(
        update={"moderation_status": "auto_deleted"}
    )
    invalid_world = world.model_copy(
        update={"comments": (bad_comment, *world.comments[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("unknown moderation status" in error for error in errors)


def test_validator_requires_at_least_two_moderation_statuses() -> None:
    world, input_data = _world()
    all_approved = tuple(
        comment.model_copy(update={"moderation_status": "approved"})
        for comment in world.comments
    )
    invalid_world = world.model_copy(update={"comments": all_approved})

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("at least two distinct moderation" in error for error in errors)


def test_validator_rejects_legal_signal_with_foreign_event() -> None:
    world, input_data = _world()
    foreign_event_id = world.countries[1].events[0].event_id
    bad_signal = world.legal_signals[0].model_copy(
        update={"event_id": foreign_event_id}
    )
    invalid_world = world.model_copy(
        update={"legal_signals": (bad_signal, *world.legal_signals[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("event from its own country" in error for error in errors)


def test_validator_rejects_document_recipe_with_empty_blocks() -> None:
    world, input_data = _world()
    bad_recipe = world.document_recipes[0].model_copy(update={"blocks": ()})
    invalid_world = world.model_copy(
        update={"document_recipes": (bad_recipe, *world.document_recipes[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("at least one block" in error for error in errors)


def test_validator_rejects_scenario_with_no_steps() -> None:
    world, input_data = _world()
    bad_scenario = world.scenarios[0].model_copy(update={"steps": ()})
    invalid_world = world.model_copy(
        update={"scenarios": (bad_scenario, *world.scenarios[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("has no steps" in error for error in errors)


def test_validator_rejects_scenario_with_dangling_related_artifact() -> None:
    world, input_data = _world()
    bad_scenario = world.scenarios[0].model_copy(
        update={"related_artifacts": ("nonexistent-artifact-id",)}
    )
    invalid_world = world.model_copy(
        update={"scenarios": (bad_scenario, *world.scenarios[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("does not exist in the world" in error for error in errors)


def test_validator_rejects_fewer_than_three_scenarios() -> None:
    world, input_data = _world()
    invalid_world = world.model_copy(update={"scenarios": world.scenarios[:2]})

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("at least 3 scenarios" in error for error in errors)


def test_validator_rejects_document_recipe_with_unknown_locale() -> None:
    world, input_data = _world()
    bad_recipe = world.document_recipes[0].model_copy(
        update={"locale": "xx-XX"}
    )
    invalid_world = world.model_copy(
        update={"document_recipes": (bad_recipe, *world.document_recipes[1:])}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any("unknown document recipe locale" in error for error in errors)


def test_validator_rejects_world_missing_a_locale_recipe() -> None:
    world, input_data = _world()
    trimmed_recipes = tuple(
        recipe for recipe in world.document_recipes if recipe.locale != "ta-IN"
    )
    invalid_world = world.model_copy(
        update={"document_recipes": trimmed_recipes}
    )

    errors = validate_world(
        invalid_world,
        forbidden_country_names=input_data.forbidden_country_names,
    )

    assert any(
        "missing a document recipe for locales" in error for error in errors
    )
