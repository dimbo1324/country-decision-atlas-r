from __future__ import annotations

import random
from scripts.synthetic_data.core.locale_corpus import (
    REQUIRED_BLOCK_IDS,
    LocaleTextPack,
)
from scripts.synthetic_data.core.world_input import (
    DocumentRecipeInput,
    TextBlockInput,
    WorldInput,
)
from scripts.synthetic_data.core.world_models import (
    ResolvedBlock,
    SyntheticCountry,
    SyntheticDocumentRecipe,
)


class DocumentRecipeError(RuntimeError):
    pass


def _humanize(metric: str) -> str:
    return metric.replace("_", " ")


def _resolve_fact(fact_path: str, *, country: SyntheticCountry) -> None:
    """Raise if a block's `requires` entry does not resolve on this country.

    Only checks presence, not the rendered value: rendering pulls the same
    facts explicitly in `_render_variant`, so a missing fact here would also
    break rendering, catching drift between a block's stated requirements
    and what it actually uses.
    """
    if fact_path == "country.name":
        if not country.name:
            raise DocumentRecipeError(f"{country.slug}: country.name is empty")
        return
    if fact_path == "country.archetype":
        if not country.archetype:
            raise DocumentRecipeError(
                f"{country.slug}: country.archetype is empty"
            )
        return
    if fact_path == "country.risks":
        if not country.risks:
            raise DocumentRecipeError(f"{country.slug}: country.risks is empty")
        return
    if fact_path == "country.strengths":
        if not country.strengths:
            raise DocumentRecipeError(
                f"{country.slug}: country.strengths is empty"
            )
        return
    raise DocumentRecipeError(
        f"{country.slug}: block requires unknown fact {fact_path!r}"
    )


def _render_variant(
    block: TextBlockInput, *, country: SyntheticCountry, rng: random.Random
) -> str:
    variant = rng.choice(block.variants)
    return variant.format(
        country=_CountryFacts(country),
        risk_label=_humanize(country.risks[0]) if country.risks else "",
        strength_label=(
            _humanize(country.strengths[0]) if country.strengths else ""
        ),
    )


class _CountryFacts:
    """Adapter exposing `{country.name}`/`{country.archetype}` placeholders."""

    def __init__(self, country: SyntheticCountry) -> None:
        self.name = country.name
        self.archetype = country.archetype.replace("_", " ")


def resolve_document_recipe(
    recipe: DocumentRecipeInput,
    *,
    world_input: WorldInput,
    country: SyntheticCountry,
    rng: random.Random,
) -> SyntheticDocumentRecipe:
    resolved_blocks: list[ResolvedBlock] = []
    for block_id in recipe.blocks:
        block = world_input.document_block_by_id(block_id)
        if "country_overview" not in block.applies_to:
            raise DocumentRecipeError(
                f"{country.slug}: block {block_id!r} does not apply to "
                "country_overview"
            )
        for fact_path in block.requires:
            _resolve_fact(fact_path, country=country)
        text = _render_variant(block, country=country, rng=rng)
        resolved_blocks.append(ResolvedBlock(block_id=block_id, text=text))
    return SyntheticDocumentRecipe(
        recipe_id=f"recipe-{country.slug}-{recipe.id}",
        document_type=recipe.id,
        country_id=country.country_id,
        blocks=tuple(resolved_blocks),
    )


def resolve_localized_document_recipe(
    *,
    country: SyntheticCountry,
    text_pack: LocaleTextPack,
    rng: random.Random,
) -> SyntheticDocumentRecipe:
    """Resolve a `country_overview` recipe from the 15-locale corpus
    (spec section 23, stage 4) rather than `world_config.json`'s
    `document_blocks`/`document_recipes` — a separate, locale-keyed block
    library so the stage 3 `en-US` recipe path stays untouched."""
    risk_label = _humanize(country.risks[0]) if country.risks else ""
    strength_label = (
        _humanize(country.strengths[0]) if country.strengths else ""
    )
    resolved_blocks = tuple(
        ResolvedBlock(
            block_id=block_id,
            text=rng.choice(text_pack.blocks[block_id]).format(
                country_name=country.name,
                risk_label=risk_label,
                strength_label=strength_label,
            ),
        )
        for block_id in REQUIRED_BLOCK_IDS
    )
    return SyntheticDocumentRecipe(
        recipe_id=f"recipe-{country.slug}-{text_pack.locale}-country_overview",
        document_type="country_overview",
        country_id=country.country_id,
        locale=text_pack.locale,
        blocks=resolved_blocks,
    )
