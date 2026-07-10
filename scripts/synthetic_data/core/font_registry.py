from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from scripts.synthetic_data.core.paths import REPO_ROOT


FONTS_DIR = REPO_ROOT / "scripts" / "synthetic_data" / "assets" / "fonts"


class FontRegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class ScriptFont:
    script: str
    font_name: str
    file_path: Path


_SCRIPT_FONTS: tuple[ScriptFont, ...] = (
    ScriptFont("Latin", "NotoSans", FONTS_DIR / "NotoSans-Regular.ttf"),
    ScriptFont("Cyrillic", "NotoSans", FONTS_DIR / "NotoSans-Regular.ttf"),
    ScriptFont(
        "Arabic", "NotoSansArabic", FONTS_DIR / "NotoSansArabic-Regular.ttf"
    ),
    ScriptFont(
        "Devanagari",
        "NotoSansDevanagari",
        FONTS_DIR / "NotoSansDevanagari-Regular.ttf",
    ),
    ScriptFont("Thai", "NotoSansThai", FONTS_DIR / "NotoSansThai-Regular.ttf"),
    ScriptFont(
        "Tamil", "NotoSansTamil", FONTS_DIR / "NotoSansTamil-Regular.ttf"
    ),
    ScriptFont(
        "Han", "NotoSansSC", FONTS_DIR / "NotoSansSC-Regular-Subset.ttf"
    ),
    ScriptFont(
        "Han/Kana", "NotoSansJP", FONTS_DIR / "NotoSansJP-Regular-Subset.ttf"
    ),
    ScriptFont(
        "Hangul", "NotoSansKR", FONTS_DIR / "NotoSansKR-Regular-Subset.ttf"
    ),
)

_FONTS_BY_SCRIPT: dict[str, ScriptFont] = {
    font.script: font for font in _SCRIPT_FONTS
}


def font_for_script(script: str) -> ScriptFont:
    """Return the embedded font asset for `script`, failing loudly if it is
    missing rather than letting a renderer silently fall back to a font
    with no glyphs for the script (spec section 8.3.4: a missing font must
    make the result unusable, not silently render as tofu boxes)."""
    font = _FONTS_BY_SCRIPT.get(script)
    if font is None:
        raise FontRegistryError(
            f"No embedded font registered for script {script!r}; "
            f"known scripts: {sorted(_FONTS_BY_SCRIPT)}"
        )
    if not font.file_path.exists():
        raise FontRegistryError(
            f"Font asset missing for script {script!r}: {font.file_path} "
            "does not exist"
        )
    return font
