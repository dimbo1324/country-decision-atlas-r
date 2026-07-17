"""Unit tests for the dev-tools script orchestrator (utils/dev_tools_scripts_runner):
registry integrity, script/category lookup, the categorized interactive menu, the
bilingual help command, non-interactive backward compatibility, JSON config
validation, and an end-to-end smoke test for the thin entry-point shim."""

from __future__ import annotations

import importlib
import json
import pytest
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch
from utils.dev_tools_scripts_runner.config_loader import ConfigLoader
from utils.dev_tools_scripts_runner.exceptions import ConfigValidationError
from utils.dev_tools_scripts_runner.main import CliApp


ROOT_DIR = Path(__file__).resolve().parents[1]

# utils/dev_tools_scripts_runner/__init__.py does `from .main import ...,
# main`, which rebinds the package's own `main` attribute to that function.
# `import utils.dev_tools_scripts_runner.main as x` resolves by attribute
# lookup on the package object and would therefore hit the function, not
# the submodule -- importlib.import_module resolves by fully-qualified
# name via sys.modules instead, sidestepping that collision.
main_module = importlib.import_module("utils.dev_tools_scripts_runner.main")


def build_app() -> CliApp:
    return CliApp()


def _capture_run_script(
    app: CliApp, monkeypatch: pytest.MonkeyPatch
) -> list[tuple[str, list[str]]]:
    calls: list[tuple[str, list[str]]] = []

    def fake_run(script: Any, extra_args: list[str]) -> int:
        calls.append((script.title, list(extra_args)))
        return 0

    monkeypatch.setattr(app.runner, "run", fake_run)
    return calls


# -- registry integrity ------------------------------------------------


def test_every_script_belongs_to_a_registered_category() -> None:
    app = build_app()

    category_keys = {category.key for category in app.registry.categories}
    for script in app.registry.scripts:
        assert script.category in category_keys, script.title


def test_every_category_has_at_least_one_script() -> None:
    app = build_app()

    for category in app.registry.categories:
        assert app.registry.scripts_in(category.key), category.key


def test_script_identifiers_are_globally_unique() -> None:
    app = build_app()

    seen: set[str] = set()
    for script in app.registry.scripts:
        for identifier in script.identifiers:
            assert identifier not in seen, (
                f"duplicate identifier: {identifier!r}"
            )
            seen.add(identifier)


def test_default_script_is_full_check() -> None:
    app = build_app()

    assert app.registry.default_script().title == "full-check"


def test_find_script_matches_title_filename_and_aliases() -> None:
    app = build_app()

    assert app.registry.find_script("format-code") is not None
    assert app.registry.find_script("format_code.py") is not None
    assert app.registry.find_script("fmt") is not None
    assert app.registry.find_script("FORMAT-CODE") is not None
    assert app.registry.find_script("does-not-exist") is None


def test_find_category_matches_key_and_both_languages() -> None:
    app = build_app()

    assert app.registry.find_category("quality") is not None
    assert app.registry.find_category("Quality Gate & Formatting") is not None
    assert (
        app.registry.find_category("Контроль качества и форматирование")
        is not None
    )
    assert app.registry.find_category("nope") is None


# -- CliApp.main: non-interactive dispatch -----------------------------


def test_main_bare_invocation_without_tty_runs_default_script_directly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression test: bare invocation used to always call input(), which
    raised EOFError whenever stdin wasn't an interactive terminal (CI,
    pre-commit hooks, subprocess pipes) — contradicting the documented
    "full quality gate (default)" behavior. It must run the default script
    directly instead."""
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)
    monkeypatch.setattr(main_module, "_stdin_is_interactive", lambda: False)

    exit_code = app.main([])

    assert exit_code == 0
    assert calls == [("full-check", [])]


def test_main_bare_invocation_with_tty_goes_interactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    monkeypatch.setattr(main_module, "_stdin_is_interactive", lambda: True)
    with patch.object(app.shell, "run", return_value=0) as interactive:
        exit_code = app.main([])

    assert exit_code == 0
    interactive.assert_called_once()


def test_main_passes_through_unmatched_flags_to_default_script(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    exit_code = app.main(["--profile", "quick"])

    assert exit_code == 0
    assert calls == [("full-check", ["--profile", "quick"])]


def test_main_dispatches_registered_script_by_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    exit_code = app.main(["sync-agents", "--check"])

    assert exit_code == 0
    assert calls == [("sync-agents", ["--check"])]


def test_main_dispatches_registered_script_by_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    exit_code = app.main(["ship", "--message", "docs: x"])

    assert exit_code == 0
    assert calls == [("ship-main", ["--message", "docs: x"])]


def test_main_help_command_prints_catalog_without_running_anything(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    exit_code = app.main(["help"])

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "full-check" in out
    assert "format-code" in out


def test_main_help_command_with_script_name_prints_manual(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    exit_code = app.main(["help", "outbox-relay"])

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "outbox-relay" in out
    assert "Kafka" in out


def test_main_help_command_respects_lang_flag(capsys: Any) -> None:
    app = build_app()

    app.main(["help", "--lang", "ru", "sync-agents"])

    out = capsys.readouterr().out
    assert "Категория:" in out


def test_main_bare_double_dash_help_shows_orchestrator_catalog(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    """`--help` alone should describe the orchestrator itself, not be
    silently forwarded to the default script's own --help."""
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    exit_code = app.main(["--help"])

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "Script manual" in out


def test_script_help_flag_still_forwards_to_the_script_itself(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`<script> --help` must still reach the script's own argparse --help
    — only a bare `--help`/`-h` is intercepted by the orchestrator."""
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    app.main(["full-check", "--help"])

    assert calls == [("full-check", ["--help"])]


# -- interactive shell ---------------------------------------------------


def test_interactive_category_then_script_prompts_for_extra_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["1", "2", "python"]):
        exit_code = app.shell.run()

    assert exit_code == 0
    assert calls == [("format-code", ["python"])]


def test_interactive_top_level_alias_shortcut_skips_category_navigation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["fmt", ""]):
        exit_code = app.shell.run()

    assert exit_code == 0
    assert calls == [("format-code", [])]


def test_interactive_empty_choice_runs_default_script(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["", ""]):
        exit_code = app.shell.run()

    assert exit_code == 0
    assert calls == [("full-check", [])]


def test_interactive_quit_exits_without_running_anything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["q"]):
        exit_code = app.shell.run()

    assert exit_code == 0
    assert calls == []


def test_interactive_unknown_choice_reprompts_instead_of_exiting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["nonsense", "q"]):
        exit_code = app.shell.run()

    assert exit_code == 0
    assert calls == []


def test_interactive_language_toggle_persists_across_menu_levels(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    app = build_app()
    _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["l", "1", "b", "q"]):
        app.shell.run()

    out = capsys.readouterr().out
    assert "Контроль качества и форматирование" in out


def test_interactive_help_browser_shows_manual_by_global_number(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    """Regression test: the digit typed in the help browser must open
    whatever the help catalog printed at that number, grouped by category
    -- not raw scripts.json declaration order. Those two orders used to
    diverge (i18n-parity/contrast-audit are "quality" scripts but were
    declared last), so typing "3" used to wrongly open ship-main instead
    of the 3rd catalog entry, i18n-parity."""
    app = build_app()
    calls = _capture_run_script(app, monkeypatch)

    with patch("builtins.input", side_effect=["h", "3", "b", "q"]):
        exit_code = app.shell.run()

    assert exit_code == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "i18n-parity" in out
    assert "en.json" in out


# -- JSON config validation (ConfigLoader) -------------------------------


def _write_config(config_dir: Path, files: dict[str, Any]) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    for filename, data in files.items():
        (config_dir / filename).write_text(json.dumps(data), encoding="utf-8")


def _base_config_files() -> dict[str, Any]:
    return {
        "categories.json": [
            {
                "key": "cat1",
                "title": {"en": "Cat One", "ru": "Категория один"},
                "blurb": {"en": "blurb", "ru": "блёрб"},
            }
        ],
        "cadences.json": {
            "weekly": {"en": "Weekly", "ru": "Еженедельно"},
        },
        "meta.json": {
            "default_script_title": "script-one",
            "default_directory": "scripts",
            "default_lang": "en",
        },
        "scripts.json": [
            {
                "title": "script-one",
                "filename": "script_one.py",
                "category": "cat1",
                "summary": {"en": "s", "ru": "s"},
                "description": {"en": "d", "ru": "d"},
                "cadence_ref": "weekly",
            }
        ],
    }


def test_config_loader_loads_a_valid_minimal_config(tmp_path: Path) -> None:
    _write_config(tmp_path, _base_config_files())

    registry = ConfigLoader(tmp_path, config_dir=tmp_path).load()

    assert registry.default_script().title == "script-one"
    assert registry.scripts_in("cat1")[0].filename == "script_one.py"


def test_config_loader_rejects_unknown_category_reference(
    tmp_path: Path,
) -> None:
    files = _base_config_files()
    files["scripts.json"][0]["category"] = "does-not-exist"
    _write_config(tmp_path, files)

    with pytest.raises(ConfigValidationError, match="unknown category"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_rejects_duplicate_script_identifiers(
    tmp_path: Path,
) -> None:
    files = _base_config_files()
    files["scripts.json"].append(
        {
            "title": "script-two",
            "filename": "script_two.py",
            "category": "cat1",
            "summary": {"en": "s2", "ru": "s2"},
            "description": {"en": "d2", "ru": "d2"},
            "cadence_ref": "weekly",
            "aliases": ["script-one"],
        }
    )
    _write_config(tmp_path, files)

    with pytest.raises(
        ConfigValidationError, match="duplicate script identifier"
    ):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_rejects_filename_with_path_separator(
    tmp_path: Path,
) -> None:
    files = _base_config_files()
    files["scripts.json"][0]["filename"] = "../evil.py"
    _write_config(tmp_path, files)

    with pytest.raises(ConfigValidationError, match="bare filename"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_rejects_directory_escaping_project_root(
    tmp_path: Path,
) -> None:
    files = _base_config_files()
    files["scripts.json"][0]["directory"] = "../outside"
    _write_config(tmp_path, files)

    with pytest.raises(ConfigValidationError, match="resolves outside"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_rejects_cadence_and_cadence_ref_together(
    tmp_path: Path,
) -> None:
    files = _base_config_files()
    files["scripts.json"][0]["cadence"] = {"en": "Daily", "ru": "Ежедневно"}
    _write_config(tmp_path, files)

    with pytest.raises(ConfigValidationError, match="pick one"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_rejects_unresolvable_cadence_ref(tmp_path: Path) -> None:
    files = _base_config_files()
    files["scripts.json"][0]["cadence_ref"] = "monthly"
    _write_config(tmp_path, files)

    with pytest.raises(ConfigValidationError, match="cadence_ref"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_reports_missing_config_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigValidationError, match="missing config file"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_reports_invalid_json(tmp_path: Path) -> None:
    files = _base_config_files()
    _write_config(tmp_path, files)
    (tmp_path / "categories.json").write_text(
        "{not valid json", encoding="utf-8"
    )

    with pytest.raises(ConfigValidationError, match="invalid JSON"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


def test_config_loader_reports_missing_required_field(tmp_path: Path) -> None:
    files = _base_config_files()
    del files["categories.json"][0]["blurb"]
    _write_config(tmp_path, files)

    with pytest.raises(ConfigValidationError, match="missing field"):
        ConfigLoader(tmp_path, config_dir=tmp_path).load()


# -- entry-point shim smoke test -----------------------------------------


def test_entry_point_shim_dispatches_help_command() -> None:
    """End-to-end smoke test for the thin `dev_tools_scripts_runner.py`
    shim itself -- every other test in this file exercises the package
    directly, so nothing else proves the two-line entry point actually
    wires argv through to `utils.dev_tools_scripts_runner.main`."""
    result = subprocess.run(
        [sys.executable, str(ROOT_DIR / "dev_tools_scripts_runner.py"), "help"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "full-check" in result.stdout
