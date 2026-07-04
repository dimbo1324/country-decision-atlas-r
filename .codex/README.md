# Codex Project Automation

This directory contains project-scoped Codex configuration for Country Decision
Atlas. It is intentionally small: durable repo rules live in `AGENTS.md`,
developer automation lives in `scripts/dev_tools`, and this directory wires
Codex to those existing project contracts.

Claude Code carries an equivalent, name-for-name mirror of the agents and
skills below under `.claude/agents/` and `.claude/skills/`, driven by
`CLAUDE.md`. Keep both sides aligned when either changes — see "Multi-Agent
Collaboration" in `AGENTS.md`/`CLAUDE.md`.

## Files

- `config.toml` — project defaults for model reasoning and subagent limits.
- `agents/` — custom agents for focused delegation.
- `skills/` — reusable project workflows for common Codex tasks.

## Recommended Codex Patterns

Use one main thread for the task owner and spawn custom agents only for
independent work:

- `country-atlas-domain-architect` — read architecture docs and extract risks.
- `country-atlas-backend-api` — implement backend/API/migration work.
- `country-atlas-frontend-web` — implement frontend and contract work.
- `country-atlas-quality-reviewer` — review the diff before finalizing.
- `country-atlas-ci-triage` — debug failed CI or local quality gates.
- `country-atlas-repo-maintainer` — formatting, docs, commits, and explicit
  publish workflows.

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
