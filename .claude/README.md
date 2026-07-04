# Claude Code Project Configuration

This directory contains project-scoped Claude Code configuration for Country
Decision Atlas. It is intentionally small: durable repo rules live in
`CLAUDE.md`, developer automation lives in `scripts/dev_tools`, and this
directory wires Claude Code to those existing project contracts.

Codex carries an equivalent, name-for-name mirror of the agents and skills
below under `.codex/agents/` and `.codex/skills/`, driven by `AGENTS.md`.
Keep both sides aligned when either changes — see "Multi-Agent Collaboration"
in `CLAUDE.md`/`AGENTS.md`.

## Files

- `launch.json` — local dev-server run targets for the `preview_*` tools
  (`web`, `web-prod`).
- `settings.json` — permission allowlist for routine read/verification
  commands, and an explicit denylist for destructive git/Docker operations.
- `agents/` — project-scoped subagents for focused delegation.
- `skills/` — reusable project workflows, invoked via the Skill tool or by the
  user typing `/<skill-name>`.

## Recommended Delegation Patterns

Do the task-owning work on the main thread; spawn a subagent only for
independent work that doesn't need the main thread's full context:

- `country-atlas-domain-architect` — read `docs/_arch_`, scope an episode,
  surface invariants and risks, before any code is written.
- `country-atlas-backend-api` — implement backend/API/migration work.
- `country-atlas-frontend-web` — implement frontend and contract-consumption
  work.
- `country-atlas-quality-reviewer` — review a diff before finalizing it.
- `country-atlas-ci-triage` — debug a failing local or CI check.
- `country-atlas-repo-maintainer` — formatting, docs upkeep, explicit publish
  workflows.

## Quality Shortcuts

```powershell
python dev_tools_scripts_runner.py format-code
python dev_tools_scripts_runner.py --profile quick
python dev_tools_scripts_runner.py --doctor
python dev_tools_scripts_runner.py ship-main --message "type: explain the change"
```

`ship-main` is only for tasks where the user explicitly requested commit and
push in the current turn. It formats, commits, verifies, fast-forwards from
`origin/main`, and pushes `main`.
