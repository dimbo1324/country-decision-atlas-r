"""The interactive REPL: top menu -> category menu -> script launch, plus
the help browser. All input() calls live here; rendering.py never reads
input and execution.py never prints menus, so each module stays testable
in isolation."""

from __future__ import annotations

from .execution import ScriptRunner
from .models import Category, ScriptInfo, Session
from .registry import ScriptRegistry
from .rendering import MenuRenderer, unknown_choice_message


_BACK_WORDS = ("b", "back", "назад")
_QUIT_WORDS = ("q", "quit", "exit", "выход")
_LANG_WORDS = ("l", "lang", "language", "язык")
_HELP_WORDS = ("h", "help", "справка")


class InteractiveShell:
    def __init__(
        self,
        registry: ScriptRegistry,
        renderer: MenuRenderer,
        runner: ScriptRunner,
    ) -> None:
        self._registry = registry
        self._renderer = renderer
        self._runner = runner

    def run(self) -> int:
        session = Session()
        while True:
            self._renderer.print_top_menu(session.lang)
            raw_choice = input(self._renderer.top_prompt(session.lang)).strip()
            lowered = raw_choice.lower()

            if not raw_choice:
                return self._runner.launch(
                    self._registry.default_script(), session.lang
                )
            if lowered in _QUIT_WORDS:
                return 0
            if lowered in _HELP_WORDS:
                self._run_help_browser(session)
                continue
            if lowered in _LANG_WORDS:
                session.toggle_lang()
                continue

            script = self._registry.find_script(raw_choice)
            if script is not None:
                return self._runner.launch(script, session.lang)

            categories = self._registry.categories
            category = (
                categories[int(raw_choice) - 1]
                if raw_choice.isdigit()
                and 1 <= int(raw_choice) <= len(categories)
                else self._registry.find_category(raw_choice)
            )
            if category is not None:
                outcome = self._run_category(category, session)
                if outcome is not None:
                    return outcome
                continue

            print(unknown_choice_message(raw_choice, session.lang))

    def _run_help_browser(self, session: Session) -> None:
        # scripts_by_category_order(), not registry.scripts (declaration
        # order) -- must match exactly what print_help_catalog numbered on
        # screen, or a typed digit opens the wrong manual.
        catalog_order = self._registry.scripts_by_category_order()
        while True:
            self._renderer.print_help_catalog(session.lang)
            raw_choice = input(self._renderer.help_prompt(session.lang)).strip()
            lowered = raw_choice.lower()

            if not raw_choice or lowered in _BACK_WORDS:
                return
            if lowered in _LANG_WORDS:
                session.toggle_lang()
                continue

            script: ScriptInfo | None = None
            if raw_choice.isdigit():
                index = int(raw_choice)
                if 1 <= index <= len(catalog_order):
                    script = catalog_order[index - 1]
            if script is None:
                script = self._registry.find_script(raw_choice)

            if script is None:
                print(unknown_choice_message(raw_choice, session.lang))
                continue
            self._renderer.print_manual(script, session.lang)

    def _run_category(self, category: Category, session: Session) -> int | None:
        """Returns an exit code once the user runs something or quits, or
        None to signal "go back to the top menu"."""
        scripts = self._registry.scripts_in(category.key)
        while True:
            self._renderer.print_category_menu(category, scripts, session.lang)
            raw_choice = input(
                self._renderer.category_prompt(session.lang)
            ).strip()
            lowered = raw_choice.lower()

            if not raw_choice or lowered in _BACK_WORDS:
                return None
            if lowered in _QUIT_WORDS:
                return 0
            if lowered in _LANG_WORDS:
                session.toggle_lang()
                continue
            if lowered in _HELP_WORDS:
                for entry in scripts:
                    self._renderer.print_manual(entry, session.lang)
                continue

            if raw_choice.isdigit():
                index = int(raw_choice)
                if 1 <= index <= len(scripts):
                    return self._runner.launch(scripts[index - 1], session.lang)
                print(unknown_choice_message(raw_choice, session.lang))
                continue

            script = self._registry.find_script(raw_choice)
            if script is not None:
                return self._runner.launch(script, session.lang)

            print(unknown_choice_message(raw_choice, session.lang))
