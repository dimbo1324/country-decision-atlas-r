# Claude Code Project Configuration

Project-scoped Claude Code configuration for Country Decision Atlas.

Durable rules live in the shared modules under `.ai/` (universal + project).
`CLAUDE.md` imports them natively via `@` syntax. Codex consumes the same
modules through the generated `AGENTS.md` (regenerate with
`python dev_tools_scripts_runner.py sync-agents`; never edit it by hand).
Subagents should read `AGENTS.md` — it is the compiled single-file ruleset.

## Files

- `launch.json` — local dev-server run targets for the `preview_*` tools.
- `settings.json` — permission allowlist for routine read/verification
  commands, and an explicit denylist for destructive git/Docker operations.
- `agents/` — project-scoped subagents for focused delegation; name-for-name
  mirror of `.codex/agents/`.
- `skills/` — reusable project workflows; mirror of `.codex/skills/`.

## Recommended delegation

Do task-owning work on the main thread; spawn a subagent only for
independent work that doesn't need the main thread's full context:

- `country-atlas-domain-architect` — read `docs/`, scope an episode,
  surface invariants and risks, before any code is written.
- `country-atlas-backend-api` — backend/API/migration work.
- `country-atlas-frontend-web` — frontend and contract-consumption work.
- `country-atlas-quality-reviewer` — review a diff before finalizing it.
- `country-atlas-ci-triage` — debug a failing local or CI check.
- `country-atlas-repo-maintainer` — formatting, docs upkeep, explicit
  publish workflows.

## Quality shortcuts

```powershell
python dev_tools_scripts_runner.py format-code
python dev_tools_scripts_runner.py --profile quick
python dev_tools_scripts_runner.py --doctor
python dev_tools_scripts_runner.py sync-agents --check
python dev_tools_scripts_runner.py ship-main --message "type: explain the change"
```

`ship-main` is only for an explicitly requested publish of already-validated
work; the default path is branch → gate → ff-merge → push.

`dev_tools_scripts_runner.py` is a thin entry-point shim only; its
implementation lives in `utils/dev_tools_scripts_runner/` — edit that
package, not the entry point, to change runner behavior.
