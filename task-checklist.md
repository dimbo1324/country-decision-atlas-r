# Task: Modularize dev_tools_scripts_runner.py

Owner request (verbatim intent): `dev_tools_scripts_runner.py` has grown to
1159 lines and will keep growing. It stays as the entry point (invocation
unchanged: `python dev_tools_scripts_runner.py ...`) but shrinks to a
near-two-line shim; all business logic and infrastructure moves into
`utils/dev_tools_scripts_runner/` following proper decomposition/modularity/
OOP/security/readability conventions. Hand-editable data currently baked
into the script (`AVAILABLE_SCRIPTS`, `CATEGORIES`, `_RECURRING_JOB_CADENCE`,
`_RECOMPUTE_CADENCE`) moves to JSON config files; Python keeps only the
business logic.

Branch: `refactor/dev-tools-runner-modularize`, fresh off `main`.

## Pre-implementation investigation (verified, not assumed)

- Full source read: 1159 lines, single file. Structure: `Text`/`Category`/
  `ScriptInfo` dataclasses (lines 1-155) → `CATEGORIES` (8 entries) →
  `AVAILABLE_SCRIPTS` (19 `ScriptInfo` entries, ~612 lines of near-identical
  repetitive data) → `Session` dataclass → lookup helpers (`find_script`,
  `find_category`, `scripts_in`, `default_script`) → rendering functions
  (`print_top_menu`, `print_category_menu`, `print_help_catalog`,
  `print_manual`) → execution functions (`run_script`, `_prompt_extra_args`,
  `_launch`) → interactive REPL (`run_interactive`, `_run_help_browser`,
  `_run_category`) → CLI entry (`main`, `run_help_command`,
  `_parse_help_args`).
- `utils/dev_tools_scripts_runner/main.py` already exists, tracked by git,
  **empty** — the owner's own placeholder marking where this work goes.
  Reused as the CLI-entry module name inside the new package.
- Data extracted programmatically (imported the live module, walked
  `CATEGORIES`/`AVAILABLE_SCRIPTS`/the two cadence constants, dumped to
  JSON) rather than hand-retyped — avoids transcription errors across ~600
  lines of bilingual text. Verified: 8 categories, 19 scripts, exact text
  match against direct reads of several entries (full-check, format-code,
  ship-main).
- Of the 19 scripts, 5 share `_RECURRING_JOB_CADENCE` verbatim and 4 share
  `_RECOMPUTE_CADENCE` verbatim (confirmed by diffing each script's cadence
  text against both constants) — JSON schema keeps these as named, reusable
  entries (`cadence_ref`) rather than flattening/duplicating the text into
  every script, preserving the DRY intent the constants already expressed.
- **Existing test file found**: `tests/test_dev_tools_scripts_runner.py`,
  26 tests, dynamically loads `dev_tools_scripts_runner.py` via
  `importlib.util.spec_from_file_location` and asserts on module-level
  attributes (`module.CATEGORIES`, `module.AVAILABLE_SCRIPTS`,
  `module.find_script`, `module.main`, `module.run_interactive`, etc.),
  monkeypatching `module.run_script`/`module._stdin_is_interactive`. This
  conflicts with a genuinely ~2-line entry point (can't cleanly re-export a
  dozen names AND stay 2 lines). Resolved by adapting the test file to
  import and exercise the new package's modules/classes directly — the
  same underlying refactor-implies-test-follows-the-code principle already
  applied to production code this session, not a coverage reduction: every
  existing assertion's intent is preserved 1:1, plus new coverage added for
  JSON config validation. A thin subprocess-level smoke test is kept for
  the entry-point shim itself so "does invoking the file still work" stays
  covered independent of the internal module structure.
- **Quality-gate wiring gap found**: `utils/` is not in
  `pyproject.toml`'s `[tool.ruff] src`, not in
  `scripts/dev_tools/format_code.py`'s `PYTHON_PATHS`, not in
  `scripts/dev_tools/full_check.py`'s `ruff check`/`mypy` invocations, and
  not matched by `.pre-commit-config.yaml`'s ruff hook file regex
  (`^(apps|packages|scripts|tests)/.*\.py$`). New code in `utils/` would
  silently sit outside the project's own quality gate unless these four
  places are updated — doing so is part of this task, not a separate one,
  since shipping unchecked code would contradict the task's own stated
  goal (proper conventions).
- `pyproject.toml`'s `[tool.setuptools.packages.find]` only looks in
  `apps/api`, `apps/worker`, `packages/contracts`, `packages/shared` for
  installable packages — `utils/` (like `scripts/`) is dev tooling run
  directly via `python <path>`, not pip-installed, so no packaging-table
  change is needed there; `sys.path[0]` is `ROOT_DIR` when the entry-point
  script is run directly (the project's own documented invocation), which
  is sufficient for `import utils.dev_tools_scripts_runner` to resolve.

## Design

- `utils/__init__.py` (new, minimal) + `utils/dev_tools_scripts_runner/`:
  - `__init__.py` — public surface: re-exports `main`.
  - `exceptions.py` — `ConfigValidationError` and friends.
  - `models.py` — `Text`, `Category`, `ScriptInfo`, `Session` (frozen
    dataclasses except `Session`; unchanged behavior from the original).
  - `config_loader.py` — `ConfigLoader`: reads the 4 JSON files, validates
    (category references resolve, `cadence`/`cadence_ref` mutually
    exclusive and resolve, no duplicate script identifiers, `filename`/
    `directory` can't escape `ROOT_DIR` via `..`), builds a
    `ScriptRegistry`. Fails fast with a clear message on bad config
    instead of a cryptic runtime `KeyError` deep in menu rendering.
  - `registry.py` — `ScriptRegistry`: owns the loaded
    categories/scripts/cadences, exposes `find_script`, `find_category`,
    `scripts_in`, `default_script` as methods instead of free functions
    over module globals.
  - `execution.py` — `ScriptRunner`: `run`, `prompt_extra_args`, `launch`
    (subprocess execution unchanged — list-form argv, no `shell=True`,
    preserved exactly).
  - `rendering.py` — `MenuRenderer`: top menu, category menu, help
    catalog, manual page — ported behavior-for-behavior.
  - `interactive.py` — `InteractiveShell`: the REPL loop, help browser,
    category browser.
  - `main.py` — `CliApp` + `main(argv)`: argv parsing/dispatch (help
    command, direct script run, interactive fallback), the module the
    owner's own empty placeholder already named.
  - `config/categories.json`, `config/cadences.json`, `config/scripts.json`,
    `config/meta.json`.
- `dev_tools_scripts_runner.py` becomes the thin shim.

## Implementation

- [ ] Finalize JSON config (with `cadence_ref` support) under
      `utils/dev_tools_scripts_runner/config/`.
- [ ] `models.py` + `exceptions.py`.
- [ ] `config_loader.py` + `registry.py`.
- [ ] `execution.py` + `rendering.py`.
- [ ] `interactive.py` + `main.py` + `__init__.py`.
- [ ] Rewrite `dev_tools_scripts_runner.py` as the thin entry point.
- [ ] Wire `utils/` into `pyproject.toml`, `format_code.py`,
      `full_check.py`, `.pre-commit-config.yaml`.
- [ ] Adapt `tests/test_dev_tools_scripts_runner.py` to the new package
      (preserve every existing assertion's intent) + add config-validation
      coverage + entry-point subprocess smoke test.
- [ ] typecheck/lint/format clean for `utils/` and the updated test file.
- [ ] `pytest tests/test_dev_tools_scripts_runner.py -v` green.
- [ ] Manual parity check: `help`, `help <script>`, direct dispatch by
      title/alias, unmatched-flags passthrough, interactive flow — output
      compared against the pre-refactor behavior.

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Final report.
