"""All user-facing text output: menus, the help catalog, and per-script
manual pages. Nothing here reads input or launches a process -- that
split keeps the REPL loop in interactive.py testable without capturing
stdout."""

from __future__ import annotations

from .models import Category, Lang, ScriptInfo
from .registry import ScriptRegistry
from pathlib import Path


def unknown_choice_message(raw_choice: str, lang: Lang) -> str:
    if lang == "ru":
        return f"\nНеизвестный выбор: {raw_choice!r}. Попробуйте снова.\n"
    return f"\nUnknown choice: {raw_choice!r}. Try again.\n"


class MenuRenderer:
    def __init__(self, registry: ScriptRegistry, root_dir: Path) -> None:
        self._registry = registry
        self._root_dir = root_dir

    # -- top menu ---------------------------------------------------------

    def print_top_menu(self, lang: Lang) -> None:
        heading = (
            "Country Decision Atlas — script orchestrator"
            if lang == "en"
            else "Country Decision Atlas — оркестратор скриптов"
        )
        print(f"\n{heading}")
        print("=" * len(heading))
        print(
            "Pick a category, or type a script's name to jump straight to it. "
            "Press Enter for the default full quality gate.\n"
            if lang == "en"
            else "Выберите категорию или введите имя скрипта, чтобы перейти к "
            "нему напрямую. Enter — quality gate по умолчанию.\n"
        )

        for index, category in enumerate(self._registry.categories, start=1):
            count = len(self._registry.scripts_in(category.key))
            print(f"{index}. {category.title.get(lang)} ({count})")
            print(f"   {category.blurb.get(lang)}")

        print()
        if lang == "en":
            print("H. Help — detailed manual for any script")
            print("L. Language: English — switch to Russian")
            print("Q. Quit")
        else:
            print("H. Help — подробное описание любого скрипта")
            print("L. Язык: русский — переключить на английский")
            print("Q. Выход")

    def top_prompt(self, lang: Lang) -> str:
        default_title = self._registry.default_script().title
        if lang == "en":
            return f"\nYour choice [default: {default_title}]: "
        return f"\nВаш выбор [по умолчанию: {default_title}]: "

    # -- category menu ------------------------------------------------

    def print_category_menu(
        self, category: Category, scripts: list[ScriptInfo], lang: Lang
    ) -> None:
        default_title = self._registry.default_script().title
        heading = category.title.get(lang)
        print(f"\n{heading}")
        print("=" * len(heading))
        for index, script in enumerate(scripts, start=1):
            default_marker = (
                " [default]" if script.title == default_title else ""
            )
            print(f"{index}. {script.title}{default_marker}")
            print(f"   {script.summary.get(lang)}")
            if script.aliases:
                label = "aliases" if lang == "en" else "алиасы"
                print(f"   {label}: {', '.join(script.aliases)}")

        print()
        if lang == "en":
            print("B. Back   H. Help   L. Language   Q. Quit")
        else:
            print("B. Назад   H. Справка   L. Язык   Q. Выход")

    def category_prompt(self, lang: Lang) -> str:
        return "\nYour choice: " if lang == "en" else "\nВаш выбор: "

    # -- help catalog + manual ------------------------------------------

    def print_help_catalog(self, lang: Lang) -> None:
        heading = "Script manual" if lang == "en" else "Справочник по скриптам"
        print(f"\n{heading}")
        print("=" * len(heading))

        number = 1
        for category in self._registry.categories:
            entries = self._registry.scripts_in(category.key)
            if not entries:
                continue
            print(f"\n{category.title.get(lang)}")
            for script in entries:
                print(
                    f"  {number:>2}. {script.title:<28} {script.summary.get(lang)}"
                )
                number += 1

        print(
            "\nType a number or script name for its full manual; B to go back."
            if lang == "en"
            else "\nВведите номер или имя скрипта для полного описания; B — назад."
        )

    def help_prompt(self, lang: Lang) -> str:
        return "\nYour choice: " if lang == "en" else "\nВаш выбор: "

    def print_manual(self, script: ScriptInfo, lang: Lang) -> None:
        print(f"\n{script.title}")
        print("-" * len(script.title))

        category = self._registry.category_for(script)
        relative_path = script.path.relative_to(self._root_dir)

        if lang == "en":
            print(f"Category: {category.title.en}")
            if script.aliases:
                print(f"Aliases:  {', '.join(script.aliases)}")
            print(f"Path:     {relative_path}")
            print(f"Cadence:  {script.cadence.en}")
            print(f"\n{script.description.en}")
            if script.examples:
                print("\nExamples:")
        else:
            print(f"Категория:     {category.title.ru}")
            if script.aliases:
                print(f"Алиасы:        {', '.join(script.aliases)}")
            print(f"Путь:          {relative_path}")
            print(f"Периодичность: {script.cadence.ru}")
            print(f"\n{script.description.ru}")
            if script.examples:
                print("\nПримеры:")

        for example in script.examples:
            command = (
                f"python dev_tools_scripts_runner.py {script.title} {example}"
            )
            print(f"  {command.rstrip()}")
