from __future__ import annotations

import pytest
from scripts.synthetic_data.core.translation_adapter import (
    TranslationAdapterError,
    generate_translation_preview,
)
from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import load_world_input
from scripts.synthetic_data.core.world_models import SyntheticWorld


def _generate_world(scale: str = "small") -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(
            seed=42017,
            profile="balanced",
            scale=scale,
            generated_on="2026-01-01",
        )
    )


def test_generates_one_record_per_source_locale_block() -> None:
    world = _generate_world()
    source_recipes = [
        recipe for recipe in world.document_recipes if recipe.locale == "en-US"
    ]
    expected_block_count = sum(len(recipe.blocks) for recipe in source_recipes)

    records = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=1
    )

    assert len(records) == expected_block_count


def test_records_never_mutate_the_source_text() -> None:
    world = _generate_world()

    records = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=1
    )

    for record in records:
        assert record.translated_text != record.source_text
        assert record.source_locale == "en-US"
        assert record.target_locale == "ar-SA"
        assert record.source_text.strip()


def test_records_carry_required_provenance_fields() -> None:
    world = _generate_world()

    records = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=7
    )

    for record in records:
        assert record.provider_name
        assert record.provider_version
        assert record.seed == 7
        assert record.generated_on
        assert record.status == "fake_synthetic_preview"
        assert record.fictional_notice == "SYNTHETIC TEST DATA - NOT REAL"


def test_translation_is_deterministic_for_the_same_seed() -> None:
    world = _generate_world()

    first = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=42
    )
    second = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=42
    )

    assert [r.translated_text for r in first] == [
        r.translated_text for r in second
    ]


def test_translation_differs_across_seeds() -> None:
    world = _generate_world()

    first = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=1
    )
    second = generate_translation_preview(
        world, source_locale="en-US", target_locale="ar-SA", seed=2
    )

    assert [r.translated_text for r in first] != [
        r.translated_text for r in second
    ]


def test_rejects_matching_source_and_target_locale() -> None:
    world = _generate_world()

    with pytest.raises(TranslationAdapterError):
        generate_translation_preview(
            world, source_locale="en-US", target_locale="en-US", seed=1
        )


def test_rejects_unknown_target_locale() -> None:
    world = _generate_world()

    with pytest.raises(TranslationAdapterError):
        generate_translation_preview(
            world, source_locale="en-US", target_locale="xx-XX", seed=1
        )


def test_rejects_source_locale_absent_from_this_worlds_recipes() -> None:
    world = _generate_world(scale="small")

    with pytest.raises(TranslationAdapterError):
        generate_translation_preview(
            world, source_locale="ru-RU", target_locale="ja-JP", seed=1
        )
