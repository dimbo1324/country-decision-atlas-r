# Country Decision Atlas — working notes for Claude Code

This file is the Claude Code entry point. All rules live in shared modules
under `.ai/` — the single source of truth for every AI assistant in this
repo. Codex reads the same modules through the generated `AGENTS.md`; never
edit that file by hand (edit a module, then run
`python dev_tools_scripts_runner.py sync-agents`).

Later modules override earlier ones; an explicit owner instruction in the
current conversation overrides everything.

## Universal rules (portable to any project)

- @.ai/universal/01-workflow.md
- @.ai/universal/02-task-checklist.md
- @.ai/universal/03-scope-and-code-style.md
- @.ai/universal/04-architecture-boundaries.md
- @.ai/universal/05-security-and-secrets.md
- @.ai/universal/06-quality-and-testing.md
- @.ai/universal/07-multi-assistant.md

## Project rules (Country Decision Atlas)

- @.ai/project/10-project-map.md
- @.ai/project/11-commands.md
- @.ai/project/12-domain-rules.md
- @.ai/project/13-progress-tracking.md

## Claude Code workspace

- `.claude/launch.json` — dev-server targets for preview tools.
- `.claude/settings.json` — permission allow/deny lists.
- `.claude/agents/` — project subagents (`country-atlas-*`) for delegated
  work; mirrors `.codex/agents/` one-to-one.
- `.claude/skills/` — reusable workflows (`project-maintenance`,
  `architecture-episode`, `ci-fix`, `code-review`); mirrors `.codex/skills/`.
