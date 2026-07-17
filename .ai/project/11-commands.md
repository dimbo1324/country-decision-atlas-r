# Project Commands and Quality Gates

All commands run from the repository root (Windows, PowerShell or Git Bash).

## Main entry point — dev tools runner

```powershell
python dev_tools_scripts_runner.py                  # full quality gate (default)
python dev_tools_scripts_runner.py --profile quick  # quick gate (pre-push minimum)
python dev_tools_scripts_runner.py format-code      # auto-format Python/frontend/Go
python dev_tools_scripts_runner.py --doctor         # read-only diagnostics
python dev_tools_scripts_runner.py sync-agents      # regenerate AGENTS.md from .ai/
python dev_tools_scripts_runner.py sync-agents --check  # verify AGENTS.md is in sync
python dev_tools_scripts_runner.py dispatch-trip-reminders  # due reminders -> outbox
python dev_tools_scripts_runner.py ship-main --message "type: why"  # guided publish
```

`ship-main` is only for an explicitly requested publish of already-validated
work; the default path is branch → gate → ff-merge → push.

`dev_tools_scripts_runner.py` itself is a thin entry-point shim only — to
change the runner's behavior (add or edit a script entry, fix a bug, adjust
the catalog), edit `utils/dev_tools_scripts_runner/` (the Python modules and
the JSON config under `utils/dev_tools_scripts_runner/config/`), not the
entry-point file.

## Direct commands (when targeting one layer)

```powershell
python -m pytest <targeted tests> -q
python -m ruff check apps packages scripts tests
python -m ruff format --check apps packages scripts tests
python -m mypy apps packages scripts tests
python -m sqlfluff lint database --dialect postgres
corepack pnpm@9.12.0 install --frozen-lockfile
corepack pnpm@9.12.0 contracts:generate
corepack pnpm@9.12.0 --filter @country-decision-atlas/web typecheck
corepack pnpm@9.12.0 --filter @country-decision-atlas/web lint
cd apps/notifier; go vet ./...; go test -race ./...
```

`-race` requires a working CGO toolchain (`CGO_ENABLED=1` plus a C
compiler). GitHub Actions' `ubuntu-latest` has one preinstalled; a local
Windows machine without mingw/gcc will fail with `-race requires cgo` —
drop `-race` for a local sanity check in that case, the CI job is the
actual `-race` gate (P2-6, Аудит-эпизод 8).

## Postgres observability (dev)

`docker-compose.yml`'s `postgres` service preloads `pg_stat_statements`
(P2-1, Аудит-эпизод 7). It still needs to be registered once per database
after the stack is up — `apply_migrations.py` doesn't do this, since a
`CREATE EXTENSION` here would fail in CI's plain `postgres:16-alpine`
service (no `shared_preload_libraries` override there), so it stays a
manual dev-only step:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Top-N slowest queries by total time:

```sql
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

`/metrics` (the FastAPI app's own endpoint) exposes request counts,
latency, and DB pool gauges separately — `pg_stat_statements` is for
diagnosing *which queries* are slow, not request-level metrics.

## Gate policy

- Before merge to `main`: full gate
  (`python dev_tools_scripts_runner.py`) must be green — it covers static
  checks, pytest, Go, Docker stack + migrations + runtime smokes, E2E,
  pre-commit.
- Quick gate (`--profile quick`) is the minimum for intermediate pushes.
- Config-only or docs-only changes still go through pre-commit hooks
  (they run automatically on commit).
- Windows note: pytest may need
  `-p no:cacheprovider --basetemp=<temp dir>` when temp-dir cleanup fights
  antivirus; the runner handles this itself.
