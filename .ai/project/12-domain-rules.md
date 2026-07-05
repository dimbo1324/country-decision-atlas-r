# Domain Rules and House Style (Country Decision Atlas)

These sharpen the universal rules for this codebase. Stricter wins.

## Code structure

- Services or repositories over ~800 lines (stricter than the universal
  1000) become a package: `__init__.py` re-exports the full previous public
  surface so external imports keep working.
- Monkeypatch safety when splitting modules: cross-cutting private helpers
  (audit, feature-flag checks, shared validators) go into one sibling
  `helpers.py`, and submodules call them by qualified module access
  (`helpers.thing(...)`), never `from .helpers import thing` — otherwise
  `monkeypatch.setattr` in tests silently stops intercepting. Run the full
  test suite immediately after any split.
- Test files use the established collision-safe abbreviations: `_repo`,
  `_dq`, `_mig`.

## Domain constraints

- Do NOT add countries or languages unless the owner explicitly asks.
- Do NOT use AI-driven translation unless the owner explicitly asks.
- Localization reads go through `app/services/localization.py`
  (`overlay_localized_fields`), never per-field branching.
- Keep legacy DB columns in place after superseding migrations.
- Feature gating via `ensure_feature_enabled(connection, key, message)`;
  new user-facing surfaces launch behind flags, disabled until acceptance.
- Missing config or an invariant violation must fail loudly — never create
  a second silent source of truth (pattern: `methodology_config.py`).

## Migrations

- Next sequential number, `NNN_short_name.sql`, one-line header comment
  (`-- Migration NNN: ...`), idempotent (`IF NOT EXISTS`,
  `ON CONFLICT DO ...`), sqlfluff-clean.
- An applied migration file is immutable: `schema_migrations` tracks exact
  filename + content checksum. Renaming/editing one is allowed only if the
  owner explicitly accepts the local database reset cost.

## Contracts

- After any API schema change: update `contracts/openapi.yaml`, run
  `pnpm contracts:generate`, commit the regenerated
  `packages/contracts/generated/types.ts`, and keep contract tests green.

## Assistant workspaces

- `.claude/agents|skills` and `.codex/agents|skills` are name-for-name
  mirrors; when one side changes, apply the equivalent change to the other
  in the same task.
- `.claude/settings.json` allowlists routine read-only commands and denies
  destructive git/Docker operations. Extend the allowlist rather than
  routing around it; never remove a deny entry without explicit owner
  approval.
