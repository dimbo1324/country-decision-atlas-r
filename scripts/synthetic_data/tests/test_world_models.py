from __future__ import annotations

from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import load_world_input
from scripts.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticWorld,
)
from typing import Any, cast


def test_synthetic_world_json_schema_is_well_formed() -> None:
    schema = SyntheticWorld.model_json_schema()

    assert schema["title"] == "SyntheticWorld"
    assert set(schema["required"]) == {"metadata", "countries"}
    metadata_ref = schema["properties"]["metadata"]
    assert "$ref" in metadata_ref or "allOf" in metadata_ref
    assert "$defs" in schema
    metadata_schema = schema["$defs"]["WorldMetadata"]
    for field in (
        "dataset_id",
        "schema_version",
        "generator_version",
        "seed",
        "profile",
        "supported_locales",
        "source_config_checksum",
        "generated_on",
        "fictional_notice",
    ):
        assert field in metadata_schema["properties"]


def test_world_metadata_carries_fictional_notice_and_locales() -> None:
    world = WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )

    assert world.metadata.fictional_notice == FICTIONAL_NOTICE
    assert world.metadata.supported_locales == ("en-US",)
    metadata = cast(dict[str, Any], world.to_dict()["metadata"])
    assert metadata["fictional_notice"] == FICTIONAL_NOTICE


def test_world_models_are_frozen() -> None:
    world = WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )

    try:
        world.metadata.seed = 1  # type: ignore[misc]
    except Exception as error:
        assert (
            "frozen" in str(error).lower() or "immutable" in str(error).lower()
        )
    else:
        raise AssertionError("expected assignment to a frozen model to fail")
