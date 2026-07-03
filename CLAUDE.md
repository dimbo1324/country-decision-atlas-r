# Country Decision Atlas — working notes for Claude Code

A full-stack decision-support platform that helps someone pick a country for a
specific goal (relocation, residency/citizenship, remote work, low-budget
living, business, safety) with structured, sourced, confidence-rated output —
not a country ranking blog. Backend is a FastAPI modular monolith, frontend is
Next.js, plus a small Go notifier service. Product vision and full domain
model live in `docs/_arch_/` (Russian) — read there before assuming intent on
anything domain-specific; this file only covers how to work in the repo.

## Layout

- `apps/api` — FastAPI backend. `app/api/v1/*` routers stay thin; business
  logic lives in `app/services/*`, SQL lives in `app/repositories/*`.
- `apps/web` — Next.js frontend.
- `apps/notifier` — Go gRPC notifier service.
- `packages/contracts/generated` — generated from `contracts/openapi.yaml` via
  `pnpm contracts:generate`. Never hand-edit.
- `database/migrations` — numbered SQL migrations (`NNN_short_name.sql`, short
  header comment describing the migration's role). Applied in order by
  `scripts/migration_runner.py`, which keys `schema_migrations` by exact
  filename and verifies a content checksum on every run — **renaming or
  editing an already-applied migration breaks tracking** for any local
  Postgres volume that already ran it (`docker compose down -v` to reset).
- `scripts/` — one-off maintenance scripts. `scripts/dev_tools/` holds scripts
  meant to be run through the orchestrator below.
- `tests/` — pytest suite, one file per concern, each with a one-line module
  docstring. `tests/e2e` is Playwright, `tests/smoke` is opt-in runtime smoke
  tests (`RUN_RUNTIME_SMOKE_TESTS=1`).

## Running the quality gate

`dev_tools_scripts_runner.py` at the repo root is a thin orchestrator: run it
with no args for an interactive menu, or with flags to forward straight to
the default script (`scripts/dev_tools/full_check.py`), e.g.:

```
python dev_tools_scripts_runner.py --profile quick   # fast local check
python dev_tools_scripts_runner.py --doctor           # read-only diagnostics
python dev_tools_scripts_runner.py                    # full gate incl. Docker/E2E
```

To add a new maintenance script: drop it in `scripts/dev_tools/`, register one
`ScriptInfo(...)` entry in `dev_tools_scripts_runner.py` — nothing else to change.

For manual/partial checks, the individual commands (also what CI and
`make quality` run):

```
python -m ruff check apps packages scripts tests
python -m ruff format --check apps packages scripts tests
python -m mypy apps packages scripts tests
python -m sqlfluff lint database --dialect postgres
python -m pytest
pnpm quality          # prettier --check, eslint, tsc, next build
python -m pre_commit run --all-files
```

Run the full set above (not just `make quality`) before merging — it also
catches SQL/formatting/pre-commit-hook drift that `make quality` skips.

## House style and hard-won conventions

- **No comments unless the WHY is genuinely non-obvious.** No docstrings
  narrating what a function does when the name already says it.
- **Services/repositories over ~800 lines get split into a package**, not a
  bigger flat file. Follow the pattern already used across the codebase
  (e.g. `services/migration_board/`, `services/data_quality/`):
  `__init__.py` re-exports the *entire* previous public surface (including
  any private `_helper` that existing tests call directly) so callers and
  tests are unaffected by the split.
- **Monkeypatch safety when splitting a module**: tests do
  `monkeypatch.setattr(some_module, "name", fn)`, which only rewrites that
  exact module object's attribute. If `name`'s call sites end up spread
  across multiple new submodules, patching one doesn't affect the others.
  Fix: put cross-cutting helpers (audit logging, feature-flag checks,
  imported functions like `overlay_localized_fields`) in one `helpers.py`
  and have every sibling submodule call them via qualified access
  (`helpers.thing(...)`), never `from .helpers import thing`. This mirrors
  the existing repository-call convention
  (`from app.repositories import X as repository`, then `repository.fn(...)`),
  which already survives this kind of split. After any such split, run the
  full test suite immediately — a stale monkeypatch target shows up as a
  real failure (AttributeError or a silently-unmocked call), not a false pass.
- **No new countries or languages, no AI-driven translation**, and **legacy
  DB columns stay in place** even after superseding migrations — these are
  standing product constraints, not oversights. Don't add them unless the
  user explicitly asks.
- Localization reads go through the read-model overlay pattern in
  `app/services/localization.py` (`overlay_localized_fields`), not ad hoc
  per-field locale branching.
- Test file names use collision-safe abbreviations where they already exist
  in the suite (`_repository`→`_repo`, `_data_quality`→`_dq`,
  `_migration`→`_mig`); every test file has a one-line module docstring
  stating what it verifies.

## Git workflow

- Branch per logical unit of work; commit per sub-task with a message
  explaining *why*, not just what.
- Run the full quality gate (section above) before merging to `main`.
- **Always ask for explicit confirmation before `git push` to `main`** — this
  project pushes directly to main (no PR gate), so a push is effectively
  irreversible from the assistant's side. Everything else (branch, commit,
  local merge) can proceed without asking.
- Prefer fast-forward merges (`git merge --ff-only`) to keep history linear.
