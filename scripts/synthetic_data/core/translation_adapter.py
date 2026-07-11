from __future__ import annotations

import random
from datetime import date
from pydantic import BaseModel, ConfigDict
from scripts.synthetic_data.core.locale_corpus import REQUIRED_LOCALES
from scripts.synthetic_data.core.seed import SeedFactory
from scripts.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticWorld,
)


FAKE_PROVIDER_NAME = "fake-shuffle-mt"
FAKE_PROVIDER_VERSION = "1"
_KNOWN_LOCALES = frozenset({"en-US", *REQUIRED_LOCALES})


class TranslationAdapterError(ValueError):
    pass


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class TranslationRecord(_FrozenModel):
    """A derived, fake-by-default translation test artifact (spec section
    8.3, translation test modes). Never mutates or replaces the
    canonical `source_text` it was built from -- it is stored alongside it,
    not instead of it -- and always carries enough provenance (provider,
    seed, status, fictional_notice) that nothing downstream can mistake it
    for a real translation or a source of truth."""

    record_id: str
    recipe_id: str
    block_id: str
    source_locale: str
    source_text: str
    target_locale: str
    translated_text: str
    provider_name: str
    provider_version: str
    seed: int
    generated_on: str
    status: str
    fictional_notice: str = FICTIONAL_NOTICE


def _fake_translate_text(
    *, source_text: str, target_locale: str, rng: random.Random
) -> str:
    """Deterministically scrambles the source text instead of performing
    any real machine translation -- offline, no network, no LLM call. The
    `[[fake-mt:...]]` marker and word-shuffle make it visually obvious this
    is not real translated content, while still producing different text
    per (seed, source, target locale) so a renderer that accidentally
    treats the translation as the source would be caught by a test."""
    words = source_text.split()
    rng.shuffle(words)
    return f"[[fake-mt:{target_locale}]] " + " ".join(words)


def generate_translation_preview(
    world: SyntheticWorld,
    *,
    source_locale: str,
    target_locale: str,
    seed: int,
    generated_on: str | None = None,
) -> tuple[TranslationRecord, ...]:
    """Builds a fake-translated preview of every document recipe block
    already generated at `source_locale`, targeting `target_locale`. This
    is deliberately a separate, opt-in step from world generation (spec
    section 8.3): canonical facts are never translated, and this adapter
    only ever reads an already-validated world, never the other way
    around."""
    if source_locale == target_locale:
        raise TranslationAdapterError(
            "source_locale and target_locale must differ"
        )
    if target_locale not in _KNOWN_LOCALES:
        raise TranslationAdapterError(
            f"unknown target_locale {target_locale!r}"
        )
    if source_locale not in _KNOWN_LOCALES:
        raise TranslationAdapterError(
            f"unknown source_locale {source_locale!r}"
        )

    seed_factory = SeedFactory(seed)
    resolved_generated_on = generated_on or date.today().isoformat()
    records = tuple(
        TranslationRecord(
            record_id=(
                f"translation-{recipe.recipe_id}-{block.block_id}-"
                f"{target_locale}"
            ),
            recipe_id=recipe.recipe_id,
            block_id=block.block_id,
            source_locale=source_locale,
            source_text=block.text,
            target_locale=target_locale,
            translated_text=_fake_translate_text(
                source_text=block.text,
                target_locale=target_locale,
                rng=seed_factory.rng(
                    "translation",
                    source_locale,
                    target_locale,
                    recipe.recipe_id,
                    block.block_id,
                ),
            ),
            provider_name=FAKE_PROVIDER_NAME,
            provider_version=FAKE_PROVIDER_VERSION,
            seed=seed,
            generated_on=resolved_generated_on,
            status="fake_synthetic_preview",
        )
        for recipe in world.document_recipes
        if recipe.locale == source_locale
        for block in recipe.blocks
    )
    if not records:
        raise TranslationAdapterError(
            f"world has no document recipes for source_locale {source_locale!r}"
        )
    return records
