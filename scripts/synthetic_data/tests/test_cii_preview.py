from __future__ import annotations

from scripts.synthetic_data.core.cii_preview import generate_cii_preview
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


def test_generates_one_preview_per_country() -> None:
    world = _generate_world()

    previews = generate_cii_preview(world, seed=1)

    assert len(previews) == len(world.countries)
    assert {preview.country_slug for preview in previews} == {
        country.slug for country in world.countries
    }


def test_metric_slugs_never_collide_with_the_real_cii_catalog() -> None:
    real_cii_slugs = {
        "rule_of_law",
        "economic_freedom",
        "political_stability",
        "safety",
        "corruption",
        "digital_access",
    }
    world = _generate_world()

    previews = generate_cii_preview(world, seed=1)

    for preview in previews:
        metric_slugs = {score.metric_slug for score in preview.metric_scores}
        assert metric_slugs.isdisjoint(real_cii_slugs)
        assert all(slug.startswith("syn_") for slug in metric_slugs)


def test_data_confidence_is_excluded_from_the_score_but_drives_confidence() -> (
    None
):
    world = _generate_world()

    previews = generate_cii_preview(world, seed=1)

    for preview in previews:
        metric_slugs = {score.metric_slug for score in preview.metric_scores}
        assert "syn_data_confidence" not in metric_slugs
        assert preview.confidence in {"high", "medium", "low"}


def test_overall_score_is_within_0_and_100() -> None:
    world = _generate_world()

    previews = generate_cii_preview(world, seed=1)

    for preview in previews:
        assert 0.0 <= preview.overall_score <= 100.0


def test_negative_polarity_metric_is_inverted() -> None:
    world = _generate_world()

    previews = generate_cii_preview(world, seed=1)

    for preview in previews:
        cost_of_living_score = next(
            score
            for score in preview.metric_scores
            if score.metric_slug == "syn_cost_of_living"
        )
        assert cost_of_living_score.normalized_value == (
            100 - cost_of_living_score.raw_value
        )


def test_preview_is_deterministic_for_the_same_world_and_seed() -> None:
    world = _generate_world()

    first = generate_cii_preview(world, seed=7, generated_on="2026-01-01")
    second = generate_cii_preview(world, seed=7, generated_on="2026-01-01")

    assert [p.model_dump(mode="json") for p in first] == [
        p.model_dump(mode="json") for p in second
    ]


def test_previews_carry_fictional_marking_and_formula_metadata() -> None:
    world = _generate_world()

    previews = generate_cii_preview(world, seed=1)

    for preview in previews:
        assert preview.fictional_notice == "SYNTHETIC TEST DATA - NOT REAL"
        assert preview.formula_version == "syn-cii-preview-v1"
        assert preview.aggregation_method == "geometric"
