from __future__ import annotations

import dataclasses
import pytest
import random
from scripts.synthetic_data.core.document_recipes import (
    DocumentRecipeError,
    resolve_document_recipe,
)
from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import (
    DocumentRecipeInput,
    TextBlockInput,
    load_world_input,
)


def test_resolve_document_recipe_binds_country_facts() -> None:
    input_data = load_world_input()
    world = WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )
    country = world.countries[0]
    recipe_input = input_data.document_recipe_by_id("country_overview")

    resolved = resolve_document_recipe(
        recipe_input,
        world_input=input_data,
        country=country,
        rng=random.Random(1),
    )

    assert resolved.country_id == country.country_id
    assert resolved.document_type == "country_overview"
    assert len(resolved.blocks) == len(recipe_input.blocks)
    for block in resolved.blocks:
        assert country.name in block.text


def test_resolve_document_recipe_is_deterministic_for_the_same_rng_seed() -> (
    None
):
    input_data = load_world_input()
    world = WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )
    country = world.countries[0]
    recipe_input = input_data.document_recipe_by_id("country_overview")

    first = resolve_document_recipe(
        recipe_input,
        world_input=input_data,
        country=country,
        rng=random.Random(7),
    )
    second = resolve_document_recipe(
        recipe_input,
        world_input=input_data,
        country=country,
        rng=random.Random(7),
    )

    assert first == second


def test_resolve_document_recipe_rejects_block_not_applicable_to_type() -> None:
    input_data = load_world_input()
    world = WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )
    country = world.countries[0]
    orphan_block = TextBlockInput(
        id="orphan_block",
        kind="paragraph",
        applies_to=("migration_report",),
        requires=(),
        variants=("A stray sentence about {country.name}.",),
    )
    patched_input = dataclasses.replace(
        input_data,
        document_blocks=(*input_data.document_blocks, orphan_block),
    )
    recipe_input = DocumentRecipeInput(
        id="broken_overview", blocks=("orphan_block",)
    )

    with pytest.raises(DocumentRecipeError, match="does not apply to"):
        resolve_document_recipe(
            recipe_input,
            world_input=patched_input,
            country=country,
            rng=random.Random(1),
        )


def test_resolve_document_recipe_rejects_unresolvable_fact() -> None:
    input_data = load_world_input()
    world = WorldGenerator(input_data=input_data).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )
    country = world.countries[0]
    bad_requires_block = TextBlockInput(
        id="bad_requires_block",
        kind="paragraph",
        applies_to=("country_overview",),
        requires=("country.population",),
        variants=("Unused variant.",),
    )
    patched_input = dataclasses.replace(
        input_data,
        document_blocks=(*input_data.document_blocks, bad_requires_block),
    )
    recipe_input = DocumentRecipeInput(
        id="broken_overview", blocks=("bad_requires_block",)
    )

    with pytest.raises(DocumentRecipeError, match="unknown fact"):
        resolve_document_recipe(
            recipe_input,
            world_input=patched_input,
            country=country,
            rng=random.Random(1),
        )
