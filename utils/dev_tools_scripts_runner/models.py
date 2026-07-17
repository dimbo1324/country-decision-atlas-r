"""Immutable data types for the dev-tools script orchestrator.

These are pure value objects -- no I/O, no config-loading knowledge.
`ConfigLoader` (config_loader.py) is the only place that turns raw JSON
into these.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


Lang = str  # "en" or "ru"
DEFAULT_LANG: Lang = "en"


@dataclass(frozen=True)
class Text:
    """A short piece of UI copy in both supported languages. English is
    the interface default; Russian is always available on request
    (`L`/`lang` in interactive mode, `--lang ru` for the `help` command)."""

    en: str
    ru: str

    def get(self, lang: Lang) -> str:
        return self.ru if lang == "ru" else self.en


@dataclass(frozen=True)
class Category:
    """A menu grouping. Scripts reference a category by `key`; the
    registry validates every reference resolves at load time."""

    key: str
    title: Text
    blurb: Text


@dataclass(frozen=True)
class ScriptInfo:
    """One entry in the script catalog. `directory` is always an already-
    resolved absolute path by the time this is constructed -- see
    `ConfigLoader._resolve_directory`."""

    title: str
    filename: str
    category: str
    summary: Text
    description: Text
    cadence: Text
    directory: Path
    aliases: tuple[str, ...] = field(default_factory=tuple)
    examples: tuple[str, ...] = field(default_factory=tuple)

    @property
    def identifiers(self) -> frozenset[str]:
        """Every string a user could type to select this script: its
        title, its filename, and any aliases -- all case-folded, since
        lookups normalize to lowercase before matching."""
        return frozenset(
            {self.title.lower(), self.filename.lower(), *self.aliases}
        )

    @property
    def path(self) -> Path:
        return self.directory / self.filename


@dataclass
class Session:
    """Mutable per-run interactive state -- currently just the display
    language, threaded through the top menu, category submenus, and the
    help browser so a language switch anywhere sticks for the rest of the
    session."""

    lang: Lang = DEFAULT_LANG

    def toggle_lang(self) -> None:
        self.lang = "ru" if self.lang == "en" else "en"
