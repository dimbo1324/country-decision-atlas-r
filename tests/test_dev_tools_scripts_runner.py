"""Unit tests for the script orchestrator: registry integrity, script/category lookup, the categorized interactive menu, the bilingual help command, and non-interactive backward compatibility."""

from __future__ import annotations

import importlib.util
import pytest
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import patch


def load_runner_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "dev_tools_scripts_runner.py"
    spec = importlib.util.spec_from_file_location(
        "dev_tools_scripts_runner", path
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _capture_run_script(
    module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> list[tuple[str, list[str]]]:
    calls: list[tuple[str, list[str]]] = []

    def fake_run_script(script: Any, args: list[str]) -> int:
        calls.append((script.title, list(args)))
        return 0

    monkeypatch.setattr(module, "run_script", fake_run_script)
    return calls


def test_every_script_belongs_to_a_registered_category() -> None:
    module = load_runner_module()

    category_keys = {category.key for category in module.CATEGORIES}
    for script in module.AVAILABLE_SCRIPTS:
        assert script.category in category_keys, script.title


def test_every_category_has_at_least_one_script() -> None:
    module = load_runner_module()

    for category in module.CATEGORIES:
        assert module.scripts_in(category.key), category.key


def test_script_identifiers_are_globally_unique() -> None:
    module = load_runner_module()

    seen: set[str] = set()
    for script in module.AVAILABLE_SCRIPTS:
        for identifier in script.identifiers:
            assert identifier not in seen, (
                f"duplicate identifier: {identifier!r}"
            )
            seen.add(identifier)


def test_default_script_is_full_check() -> None:
    module = load_runner_module()

    assert module.default_script().title == "full-check"


def test_find_script_matches_title_filename_and_aliases() -> None:
    module = load_runner_module()

    assert module.find_script("format-code") is not None
    assert module.find_script("format_code.py") is not None
    assert module.find_script("fmt") is not None
    assert module.find_script("FORMAT-CODE") is not None
    assert module.find_script("does-not-exist") is None


def test_find_category_matches_key_and_both_languages() -> None:
    module = load_runner_module()

    assert module.find_category("quality") is not None
    assert module.find_category("Quality Gate & Formatting") is not None
    assert (
        module.find_category("Контроль качества и форматирование") is not None
    )
    assert module.find_category("nope") is None


def test_main_bare_invocation_without_tty_runs_default_script_directly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression test: bare invocation used to always call input(), which
    raised EOFError whenever stdin wasn't an interactive terminal (CI,
    pre-commit hooks, subprocess pipes) — contradicting the documented
    "full quality gate (default)" behavior. It must now run the default
    script directly instead."""
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)
    monkeypatch.setattr(module, "_stdin_is_interactive", lambda: False)

    exit_code = module.main([])

    assert exit_code == 0
    assert calls == [("full-check", [])]


def test_main_bare_invocation_with_tty_goes_interactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    monkeypatch.setattr(module, "_stdin_is_interactive", lambda: True)
    with patch.object(module, "run_interactive", return_value=0) as interactive:
        exit_code = module.main([])

    assert exit_code == 0
    interactive.assert_called_once()


def test_main_passes_through_unmatched_flags_to_default_script(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    exit_code = module.main(["--profile", "quick"])

    assert exit_code == 0
    assert calls == [("full-check", ["--profile", "quick"])]


def test_main_dispatches_registered_script_by_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    exit_code = module.main(["sync-agents", "--check"])

    assert exit_code == 0
    assert calls == [("sync-agents", ["--check"])]


def test_main_dispatches_registered_script_by_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    exit_code = module.main(["ship", "--message", "docs: x"])

    assert exit_code == 0
    assert calls == [("ship-main", ["--message", "docs: x"])]


def test_main_help_command_prints_catalog_without_running_anything(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    exit_code = module.main(["help"])

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "full-check" in out
    assert "format-code" in out


def test_main_help_command_with_script_name_prints_manual(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    exit_code = module.main(["help", "outbox-relay"])

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "outbox-relay" in out
    assert "Kafka" in out


def test_main_help_command_respects_lang_flag(capsys: Any) -> None:
    module = load_runner_module()

    module.main(["help", "--lang", "ru", "sync-agents"])

    out = capsys.readouterr().out
    assert "Категория:" in out


def test_main_bare_double_dash_help_shows_orchestrator_catalog(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    """`--help` alone should describe the orchestrator itself, not be
    silently forwarded to the default script's own --help."""
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    exit_code = module.main(["--help"])

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "Script manual" in out


def test_script_help_flag_still_forwards_to_the_script_itself(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`<script> --help` must still reach the script's own argparse --help
    — only a bare `--help`/`-h` is intercepted by the orchestrator."""
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    module.main(["full-check", "--help"])

    assert calls == [("full-check", ["--help"])]


def test_interactive_category_then_script_prompts_for_extra_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["1", "2", "python"]):
        exit_code = module.run_interactive()

    assert exit_code == 0
    assert calls == [("format-code", ["python"])]


def test_interactive_top_level_alias_shortcut_skips_category_navigation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["fmt", ""]):
        exit_code = module.run_interactive()

    assert exit_code == 0
    assert calls == [("format-code", [])]


def test_interactive_empty_choice_runs_default_script(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["", ""]):
        exit_code = module.run_interactive()

    assert exit_code == 0
    assert calls == [("full-check", [])]


def test_interactive_quit_exits_without_running_anything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["q"]):
        exit_code = module.run_interactive()

    assert exit_code == 0
    assert calls == []


def test_interactive_unknown_choice_reprompts_instead_of_exiting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["nonsense", "q"]):
        exit_code = module.run_interactive()

    assert exit_code == 0
    assert calls == []


def test_interactive_language_toggle_persists_across_menu_levels(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    module = load_runner_module()
    _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["l", "1", "b", "q"]):
        module.run_interactive()

    out = capsys.readouterr().out
    assert "Контроль качества и форматирование" in out


def test_interactive_help_browser_shows_manual_by_global_number(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    module = load_runner_module()
    calls = _capture_run_script(module, monkeypatch)

    with patch("builtins.input", side_effect=["h", "3", "b", "q"]):
        exit_code = module.run_interactive()

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "ship-main" in out
    assert "Requires --message" in out
