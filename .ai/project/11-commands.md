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
cd apps/notifier; go vet ./...; go test ./...
```

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
