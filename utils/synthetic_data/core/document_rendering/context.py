from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from utils.synthetic_data.core.locale_corpus import LocaleTextPack
from utils.synthetic_data.core.world_models import (
    SyntheticCountry,
    SyntheticDocumentRecipe,
    SyntheticWorld,
)


@dataclass(frozen=True)
class RenderContext:
    world: SyntheticWorld
    recipe: SyntheticDocumentRecipe
    country: SyntheticCountry
    text_pack: LocaleTextPack

    @property
    def locale(self) -> str:
        return self.recipe.locale

    @property
    def is_rtl(self) -> bool:
        return self.text_pack.is_rtl

    @property
    def script(self) -> str:
        return self.text_pack.profile.script

    @property
    def marker_lines(self) -> tuple[str, str]:
        """The fixed English technical marker plus the locale's translated
        notice, both required on every artifact (spec section 15)."""
        from utils.synthetic_data.core.world_models import FICTIONAL_NOTICE

        return (FICTIONAL_NOTICE, self.text_pack.fictional_notice)


@dataclass(frozen=True)
class GeneratedDocument:
    path: Path
    file_format: str
    mode: str
    locale: str
    country_id: str
    recipe_id: str
    related_artifact_ids: tuple[str, ...]
    size_bytes: int
