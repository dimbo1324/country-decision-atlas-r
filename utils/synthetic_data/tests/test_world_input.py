from __future__ import annotations

import json
import pytest
from pathlib import Path
from typing import cast
from utils.synthetic_data.core.paths import DEFAULT_WORLD_INPUT_FILE
from utils.synthetic_data.core.world_input import (
    REQUIRED_METRICS,
    WorldInputError,
    load_world_input,
)


def _read_default_payload() -> dict[str, object]:
    payload = json.loads(DEFAULT_WORLD_INPUT_FILE.read_text(encoding="utf-8"))
    return cast(dict[str, object], payload)


def _write_world_input(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "world_config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _existing_name_prefixes(payload: dict[str, object]) -> list[str]:
    return cast(list[str], payload["name_prefixes"])


def test_default_world_input_loads_all_archetypes_and_profiles() -> None:
    world_input = load_world_input()

    assert world_input.schema_version == "1.0"
    assert world_input.default_country_count == 5
    assert len(world_input.archetypes) == 5
    assert {profile.slug for profile in world_input.profiles} == {
        "balanced",
        "crisis",
        "data_quality",
        "moderation",
        "optimistic",
    }
    assert set(world_input.archetypes[0].metric_ranges) == set(REQUIRED_METRICS)


def test_default_world_input_loads_content_libraries() -> None:
    world_input = load_world_input()

    assert len(world_input.user_given_names) >= 5
    assert len(world_input.user_family_names) >= 5
    assert world_input.document_blocks
    assert world_input.document_recipes
    recipe = world_input.document_recipe_by_id("country_overview")
    assert recipe.blocks
    for block_id in recipe.blocks:
        block = world_input.document_block_by_id(block_id)
        assert block.variants


def test_document_recipe_referencing_unknown_block_is_rejected(
    tmp_path: Path,
) -> None:
    payload = _read_default_payload()
    recipes = payload["document_recipes"]
    assert isinstance(recipes, list)
    first_recipe = recipes[0]
    assert isinstance(first_recipe, dict)
    first_recipe["blocks"] = ["missing_block"]

    with pytest.raises(WorldInputError, match="unknown blocks"):
        load_world_input(_write_world_input(tmp_path, payload))


def test_duplicate_document_block_id_is_rejected(tmp_path: Path) -> None:
    payload = _read_default_payload()
    blocks = payload["document_blocks"]
    assert isinstance(blocks, list)
    first_block = blocks[0]
    assert isinstance(first_block, dict)
    duplicate = dict(first_block)
    blocks.append(duplicate)

    with pytest.raises(WorldInputError, match="unique"):
        load_world_input(_write_world_input(tmp_path, payload))


def test_missing_required_metric_is_rejected(tmp_path: Path) -> None:
    payload = _read_default_payload()
    archetypes = payload["archetypes"]
    assert isinstance(archetypes, list)
    first_archetype = archetypes[0]
    assert isinstance(first_archetype, dict)
    metric_ranges = first_archetype["metric_ranges"]
    assert isinstance(metric_ranges, dict)
    metric_ranges.pop("safety")

    with pytest.raises(WorldInputError, match="required metrics"):
        load_world_input(_write_world_input(tmp_path, payload))


def test_unknown_profile_archetype_is_rejected(tmp_path: Path) -> None:
    payload = _read_default_payload()
    profiles = payload["profiles"]
    assert isinstance(profiles, list)
    first_profile = profiles[0]
    assert isinstance(first_profile, dict)
    profile_archetypes = first_profile["archetypes"]
    assert isinstance(profile_archetypes, list)
    profile_archetypes[0] = "missing_archetype"

    with pytest.raises(WorldInputError, match="unknown archetypes"):
        load_world_input(_write_world_input(tmp_path, payload))


@pytest.mark.parametrize(
    "unsafe_value",
    [
        "contact-owner@example.com",
        "https://internal.example.com/admin",
        "ftp://files.example.com",
        "production password: hunter2",
        "AUTH_TOKEN=abc123",
    ],
)
def test_input_containing_pii_or_secrets_is_rejected(
    tmp_path: Path, unsafe_value: str
) -> None:
    payload = _read_default_payload()
    payload["name_prefixes"] = [
        unsafe_value,
        *_existing_name_prefixes(payload),
    ]

    with pytest.raises(WorldInputError):
        load_world_input(_write_world_input(tmp_path, payload))


def test_pii_in_user_given_names_is_rejected(tmp_path: Path) -> None:
    payload = _read_default_payload()
    payload["user_given_names"] = [
        "contact-owner@example.com",
        *cast(list[str], payload["user_given_names"]),
    ]

    with pytest.raises(WorldInputError):
        load_world_input(_write_world_input(tmp_path, payload))


def test_secret_keyword_in_document_block_variant_is_rejected(
    tmp_path: Path,
) -> None:
    payload = _read_default_payload()
    blocks = payload["document_blocks"]
    assert isinstance(blocks, list)
    first_block = blocks[0]
    assert isinstance(first_block, dict)
    variants = first_block["variants"]
    assert isinstance(variants, list)
    variants.append("production password: hunter2")

    with pytest.raises(WorldInputError):
        load_world_input(_write_world_input(tmp_path, payload))


def test_synthetic_scheme_urls_are_allowed(tmp_path: Path) -> None:
    payload = _read_default_payload()
    payload["name_prefixes"] = [
        "synthetic://internal-note",
        *_existing_name_prefixes(payload),
    ]

    # Should not raise: the synthetic:// scheme is the generator's own
    # placeholder scheme, not a real network address.
    load_world_input(_write_world_input(tmp_path, payload))
