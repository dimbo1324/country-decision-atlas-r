"""Loads and validates the JSON config that drives the script catalog.

Config is hand-edited (that's the whole point of moving it out of Python),
so every check here exists to turn a bad edit into one clear, immediate
error message instead of a cryptic KeyError/AttributeError surfacing deep
inside menu rendering or, worse, a subprocess launch resolving to the
wrong file.
"""

from __future__ import annotations

import json
from .exceptions import ConfigValidationError
from .models import Category, ScriptInfo, Text
from .registry import ScriptRegistry
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(__file__).resolve().parent / "config"


class ConfigLoader:
    def __init__(self, root_dir: Path, config_dir: Path = CONFIG_DIR) -> None:
        self._root_dir = root_dir.resolve()
        self._config_dir = config_dir

    def load(self) -> ScriptRegistry:
        categories = self._load_categories()
        cadences = self._load_cadences()
        meta = self._load_meta()
        scripts = self._load_scripts(categories, cadences, meta)
        return ScriptRegistry(
            categories=categories,
            scripts=scripts,
            default_script_title=meta["default_script_title"],
        )

    # -- top-level file loaders ------------------------------------------

    def _read_json(self, filename: str) -> Any:
        path = self._config_dir / filename
        if not path.exists():
            raise ConfigValidationError(f"missing config file: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigValidationError(
                f"invalid JSON in {path}: {exc}"
            ) from exc

    def _load_categories(self) -> list[Category]:
        raw = self._read_json("categories.json")
        if not isinstance(raw, list):
            raise ConfigValidationError("categories.json must be a JSON array")

        categories: list[Category] = []
        seen_keys: set[str] = set()
        for index, entry in enumerate(raw):
            where = f"categories.json[{index}]"
            self._require_fields(entry, ("key", "title", "blurb"), where)
            key = entry["key"]
            if key in seen_keys:
                raise ConfigValidationError(
                    f"{where}: duplicate category key {key!r}"
                )
            seen_keys.add(key)
            categories.append(
                Category(
                    key=key,
                    title=self._text(entry["title"], f"{where}.title"),
                    blurb=self._text(entry["blurb"], f"{where}.blurb"),
                )
            )
        if not categories:
            raise ConfigValidationError(
                "categories.json declares no categories"
            )
        return categories

    def _load_cadences(self) -> dict[str, Text]:
        raw = self._read_json("cadences.json")
        if not isinstance(raw, dict):
            raise ConfigValidationError("cadences.json must be a JSON object")
        return {
            key: self._text(value, f"cadences.json[{key!r}]")
            for key, value in raw.items()
        }

    def _load_meta(self) -> dict[str, str]:
        raw = self._read_json("meta.json")
        if not isinstance(raw, dict):
            raise ConfigValidationError("meta.json must be a JSON object")
        self._require_fields(
            raw,
            ("default_script_title", "default_directory", "default_lang"),
            "meta.json",
        )
        return raw

    def _load_scripts(
        self,
        categories: list[Category],
        cadences: dict[str, Text],
        meta: dict[str, str],
    ) -> list[ScriptInfo]:
        raw = self._read_json("scripts.json")
        if not isinstance(raw, list):
            raise ConfigValidationError("scripts.json must be a JSON array")

        category_keys = {c.key for c in categories}
        default_directory = meta["default_directory"]

        scripts: list[ScriptInfo] = []
        seen_identifiers: set[str] = set()
        for index, entry in enumerate(raw):
            where = f"scripts.json[{index}]"
            self._require_fields(
                entry,
                ("title", "filename", "category", "summary", "description"),
                where,
            )

            category = entry["category"]
            if category not in category_keys:
                raise ConfigValidationError(
                    f"{where}: unknown category {category!r} "
                    f"(known: {sorted(category_keys)})"
                )

            filename = entry["filename"]
            self._require_bare_filename(filename, where)

            script = ScriptInfo(
                title=entry["title"],
                filename=filename,
                category=category,
                summary=self._text(entry["summary"], f"{where}.summary"),
                description=self._text(
                    entry["description"], f"{where}.description"
                ),
                cadence=self._resolve_cadence(entry, cadences, where),
                directory=self._resolve_directory(
                    entry.get("directory", default_directory), where
                ),
                aliases=tuple(entry.get("aliases", [])),
                examples=tuple(entry.get("examples", [])),
            )

            for identifier in script.identifiers:
                if identifier in seen_identifiers:
                    raise ConfigValidationError(
                        f"{where}: duplicate script identifier {identifier!r} "
                        "-- every title/filename/alias must be globally unique"
                    )
                seen_identifiers.add(identifier)

            scripts.append(script)

        if not scripts:
            raise ConfigValidationError("scripts.json declares no scripts")
        return scripts

    # -- field-level helpers ----------------------------------------------

    def _require_fields(
        self, entry: Any, fields: tuple[str, ...], where: str
    ) -> None:
        if not isinstance(entry, dict):
            raise ConfigValidationError(f"{where}: expected a JSON object")
        missing = [f for f in fields if f not in entry]
        if missing:
            raise ConfigValidationError(f"{where}: missing field(s) {missing}")

    def _text(self, raw: Any, where: str) -> Text:
        if not isinstance(raw, dict) or "en" not in raw or "ru" not in raw:
            raise ConfigValidationError(
                f"{where}: expected an object with 'en' and 'ru' string keys"
            )
        return Text(en=raw["en"], ru=raw["ru"])

    def _resolve_cadence(
        self, entry: dict[str, Any], cadences: dict[str, Text], where: str
    ) -> Text:
        has_inline = "cadence" in entry
        has_ref = "cadence_ref" in entry
        if has_inline and has_ref:
            raise ConfigValidationError(
                f"{where}: has both 'cadence' and 'cadence_ref' -- pick one"
            )
        if has_ref:
            ref = entry["cadence_ref"]
            if ref not in cadences:
                raise ConfigValidationError(
                    f"{where}: cadence_ref {ref!r} not found in cadences.json "
                    f"(known: {sorted(cadences)})"
                )
            return cadences[ref]
        if has_inline:
            return self._text(entry["cadence"], f"{where}.cadence")
        raise ConfigValidationError(
            f"{where}: must set either 'cadence' or 'cadence_ref'"
        )

    def _require_bare_filename(self, filename: str, where: str) -> None:
        if (
            not filename
            or "/" in filename
            or "\\" in filename
            or ".." in filename
        ):
            raise ConfigValidationError(
                f"{where}: filename {filename!r} must be a bare filename "
                "(no path separators or '..')"
            )

    def _resolve_directory(self, relative: str, where: str) -> Path:
        # Reject anything that would resolve outside the project root
        # (e.g. a stray "../.." in a bad hand-edit) rather than silently
        # building a path that could launch an arbitrary file elsewhere
        # on disk.
        candidate = (self._root_dir / relative).resolve()
        try:
            candidate.relative_to(self._root_dir)
        except ValueError as exc:
            raise ConfigValidationError(
                f"{where}: directory {relative!r} resolves outside the "
                "project root"
            ) from exc
        return candidate
