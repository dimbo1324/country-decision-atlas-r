"""ScriptRegistry: an in-memory, queryable view over the loaded script
catalog. Built once by ConfigLoader; read-only afterwards."""

from __future__ import annotations

from .exceptions import RunnerError
from .models import Category, ScriptInfo


class ScriptRegistry:
    def __init__(
        self,
        categories: list[Category],
        scripts: list[ScriptInfo],
        default_script_title: str,
    ) -> None:
        self._categories = categories
        self._scripts = scripts
        self._default_script_title = default_script_title

    @property
    def categories(self) -> list[Category]:
        return list(self._categories)

    @property
    def scripts(self) -> list[ScriptInfo]:
        return list(self._scripts)

    def find_script(self, choice: str) -> ScriptInfo | None:
        normalized = choice.strip().lower()
        for script in self._scripts:
            if normalized in script.identifiers:
                return script
        return None

    def find_category(self, choice: str) -> Category | None:
        normalized = choice.strip().lower()
        for category in self._categories:
            names = {
                category.key,
                category.title.en.lower(),
                category.title.ru.lower(),
            }
            if normalized in names:
                return category
        return None

    def scripts_in(self, category_key: str) -> list[ScriptInfo]:
        return [s for s in self._scripts if s.category == category_key]

    def scripts_by_category_order(self) -> list[ScriptInfo]:
        """All scripts, grouped by category in category-declaration order
        (full-check, format-code, ..., then the next category's scripts,
        ...) -- the exact order the help catalog numbers and prints them
        in. This is the single source of truth for "the Nth entry" so a
        digit typed in the help browser always opens the Nth entry it
        actually saw on screen, never a different one picked by
        `scripts.json`'s raw declaration order (those two orders drift
        apart the moment a script isn't declared next to the rest of its
        category, e.g. i18n-parity/contrast-audit are both "quality" but
        declared last -- this was a real bug in the pre-refactor code,
        confirmed against a fresh render diff, not a hypothetical one)."""
        ordered: list[ScriptInfo] = []
        for category in self._categories:
            ordered.extend(self.scripts_in(category.key))
        return ordered

    def default_script(self) -> ScriptInfo:
        script = self.find_script(self._default_script_title)
        if script is None:
            raise RunnerError(
                f"default_script_title {self._default_script_title!r} in "
                "meta.json does not match any registered script"
            )
        return script

    def category_for(self, script: ScriptInfo) -> Category:
        for category in self._categories:
            if category.key == script.category:
                return category
        # ConfigLoader validates every script's category reference at load
        # time, so reaching here means the registry was built by hand
        # (e.g. in a test) with inconsistent data.
        raise RunnerError(
            f"script {script.title!r} references unknown category "
            f"{script.category!r}"
        )
