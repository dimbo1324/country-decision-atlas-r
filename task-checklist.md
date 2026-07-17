# Task: Synthetic data — Stage 0 relocation (scripts/synthetic_data -> utils/synthetic_data)

Owner request (verbatim intent): execute Stage 0 of
`docs/_arch_/SYNTHETIC_DATA_PLAN.md` in full, without stopping to ask at
each step — move files, delete/add/update what the plan calls for, update
`.gitignore`, and land the infrastructure so future synthetic-data work
never has to think about plumbing again.

Branch: `refactor/synthetic-data-relocate`, off up-to-date `main`.

Process note (honest deviation): per the owner's explicit "do the whole
stage, don't ask at each step" instruction, this checklist was written
**after** the work instead of committed before starting per
`.ai/universal/02-task-checklist.md`'s normal protocol. Recorded here so
the deviation is visible, not silent.

## What Stage 0 required (from the plan)

1. `git mv scripts/synthetic_data utils/synthetic_data`.
2. Rename every `scripts.synthetic_data` / `scripts/synthetic_data`
   reference to `utils.synthetic_data` / `utils/synthetic_data`.
3. Move `docs/synthetic_data/input_data/*.json` into
   `utils/synthetic_data/input_data/`; fix `core/paths.py`.
4. New default output root `.synthetic_data/` (gitignored) instead of
   `docs/synthetic_data/output_data/`.
5. New thin entry point `scripts/synthetic_data.py` (<=10 lines of logic).
6. Fix every piece of obvery obvery — `full_check.py`'s dedicated pytest
   step, `pyproject.toml`, `.pre-commit-config.yaml`, docs.
7. Register `synthetic-data` in
   `utils/dev_tools_scripts_runner/config/scripts.json`.
8. (Optional per plan, explicitly deferred here — see below.)
9. Delete `docs/synthetic_data/` entirely.

## Implementation

- [+] `git mv scripts/synthetic_data utils/synthetic_data` — hit an
      unexpected snag: pre-existing, untracked, completely empty stub
      directories (`core`, `archive`, `assets`, `generators`,
      `mock_server`, `tests`) already sat under `utils/synthetic_data/`,
      so `git mv` nested the real package one level too deep
      (`utils/synthetic_data/synthetic_data/...`). Confirmed every stray
      directory held zero files (`find -type f`) before removing them
      (owner explicitly approved the `rm -rf`/`rmdir` once flagged), then
      flattened the real content back up to `utils/synthetic_data/*`.
      Verified via `git status` that all 117 files show as clean `R`
      renames from their original `scripts/synthetic_data/...` path, none
      routed through the stray nested path.
- [+] Bulk-renamed `scripts.synthetic_data` -> `utils.synthetic_data` and
      `scripts/synthetic_data` -> `utils/synthetic_data` across every
      `.py`/`.md` file inside the moved package (sed over the whole tree,
      then a full-repo grep swept for stragglers).
- [+] `core/paths.py` rewritten: `PACKAGE_ROOT` (new) = the package's own
      directory, `DEFAULT_INPUT_DATA_DIR` now lives under it
      (`utils/synthetic_data/input_data/`); `DEFAULT_OUTPUT_DATA_ROOT` now
      `REPO_ROOT / ".synthetic_data"`. `SYNTHETIC_DATA_ROOT` (the old
      `docs/synthetic_data` constant) removed — confirmed nothing outside
      `paths.py` imported it directly.
- [+] `core/font_registry.py`'s `FONTS_DIR` fixed by hand (`"scripts"` ->
      `"utils"` path segment) — the one hardcoded path split across
      separate string literals that the bulk sed couldn't catch.
- [+] `git mv docs/synthetic_data/input_data utils/synthetic_data/input_data`;
      confirmed `docs/synthetic_data/` held zero files afterward and
      removed the now-empty directory tree.
- [+] `scripts/synthetic_data.py` created (thin shim, matches
      `dev_tools_scripts_runner.py`'s own pattern) — but a bare copy of
      that pattern doesn't work one directory level down: `sys.path[0]`
      for `python scripts/synthetic_data.py` is `scripts/`, not the repo
      root, so `from utils.synthetic_data.cli import main` raised
      `ModuleNotFoundError`. Fixed by matching the established pattern
      already used by other `scripts/*.py` entry points
      (`scripts/apply_migrations.py`): insert `ROOT_DIR` onto `sys.path`
      before the first-party import, `# noqa: E402` on that one line.
- [+] `.gitignore`: `docs/synthetic_data/output_data/` -> `.synthetic_data/`.
- [+] `scripts/dev_tools/full_check.py`: the dedicated
      `pytest (scripts/synthetic_data)` gate step renamed to
      `pytest (utils/synthetic_data)`, path updated to
      `utils/synthetic_data/tests`.
- [+] `utils/dev_tools_scripts_runner/config/scripts.json`: full-check's
      own description text (`scripts/synthetic_data` mention) fixed; new
      `synthetic-data` entry added (`filename: synthetic_data.py`,
      `directory: scripts` override, aliases `synth`/`syn-data`, category
      `synthetic`) so the pipeline is runnable through the orchestrator
      (`python dev_tools_scripts_runner.py synthetic-data <args>`).
- [+] `utils/dev_tools_scripts_runner/config/categories.json`: new
      `synthetic` category added ("Synthetic Data Pipeline") — deliberately
      *not* folded into the existing `demo` category, since that one's
      blurb is specifically scoped to the conserved real demo countries
      (russia/uruguay/argentina), a different concept from a fictional
      generated world.
- [+] Docs updated to the new paths: root `README.md` (repo map row, mock
      server invocation, doc-links section), `docs/_arch_/01_Продукт/`
      `02_Текущее_состояние_системы.md` §7.3, `docs/_arch_/08_Открытые_вопросы.md`
      Р-11. Package's own `utils/synthetic_data/README.md`: every
      `docs/synthetic_data/...` input/output path reference fixed, every
      `python -m scripts.synthetic_data.cli ...` / `python -m utils.synthetic_data.cli ...`
      invocation example in the CLI reference switched to the new
      canonical `python scripts/synthetic_data.py ...` form (mock_server
      invocation correctly stays `python -m utils.synthetic_data.mock_server`
      -- no shim exists for it, out of Stage 0 scope). Stale ТЗ-file path
      reference removed (that file no longer exists under `docs/`).
- [+] `pyproject.toml` / `.pre-commit-config.yaml` checked for stale
      `scripts/synthetic_data` references — none found; both already cover
      `utils/` generically from the prior `dev_tools_scripts_runner`
      modularization task, so no edit was needed here.
- [+] `.claude/`, `.codex/` checked for `synthetic` mentions — none found,
      nothing to update.
- [ ] Optional gate flag from the plan (`--with-synthetic` smoke phase in
      `full_check.py`, off by default) — **deliberately deferred, not
      implemented.** The plan itself marks it optional; adding a new CLI
      flag and gate phase is feature work beyond "relocate and fix
      references," and the existing dedicated
      `pytest (utils/synthetic_data)` step already keeps the pipeline
      covered without it. Flagged here so it isn't silently forgotten.

## Verification

- [+] `git status` after `git add -A`: 117 clean renames (zero routed
      through the stray nested path) + 3 more renames (input_data) + 8
      modified/added files — matches the file set actually touched, no
      stray files.
- [+] Repo-wide grep for `scripts.synthetic_data` / `scripts/synthetic_data` /
      `docs/synthetic_data` (outside historical "moved from" notes and the
      plan doc itself): clean.
- [+] `py -3.12 -m pytest utils/synthetic_data/tests -q` — all tests green
      (exit code 0; ~302 tests per the package's own README).
- [+] `python -m ruff check utils/synthetic_data scripts/synthetic_data.py`
      — 14 `I001` import-order errors surfaced after the module rename
      (same class of issue hit during the `dev_tools_scripts_runner`
      modularization), fixed via `--fix`, re-verified clean.
- [+] `python -m ruff format --check` — 1 file needed reformatting
      (`cli.py`, from an earlier manual help-text edit), fixed, re-verified.
- [+] `python -m mypy utils/synthetic_data scripts/synthetic_data.py` —
      clean, no issues.
- [+] Manual smoke tests via the new entry point: `validate` (schema
      check, no I/O), `generate --formats json --scale small --seed
      42017` (full dataset write, confirmed output landed under
      `.synthetic_data/<dataset_id>/` at the repo root, confirmed
      git-ignored, cleaned up afterward).
- [+] Dispatch through the orchestrator verified:
      `python dev_tools_scripts_runner.py help synthetic-data` (catalog
      entry renders correctly) and
      `python dev_tools_scripts_runner.py synthetic-data validate` (actual
      subprocess dispatch works, including with the default `python`
      interpreter, not just the `py -3.12` one the heavier document-format
      dependencies are installed under -- confirmed by the pipeline's own
      lazy-import design: `validate`/`plan`/`list`/`prune`/`schema` never
      import the heavy optional deps).
- [-] Full project quality gate (`python dev_tools_scripts_runner.py`,
      Docker stack + E2E) was **not** re-run end-to-end for this task —
      the prior task's full run already exercised the
      `pytest (utils/synthetic_data)` gate step at its old path/name
      shape; this task re-verified the equivalent command directly
      (see above) rather than re-running the full ~10-minute Docker/E2E
      gate for a pure-relocation change with no Docker/API/frontend
      surface. Flagged honestly rather than silently claiming full-gate
      coverage.

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report (in chat).
