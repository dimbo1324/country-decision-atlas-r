---
name: project-maintenance
description: Use for routine Country Decision Atlas maintenance: formatting, quality gates, commits, and pushing explicitly requested work to main.
---

# Project Maintenance

Use repository automation before hand-written command sequences.

## Fast Paths

Format all code:

```powershell
python dev_tools_scripts_runner.py format-code
```

Run the quick local quality gate:

```powershell
python dev_tools_scripts_runner.py --profile quick
```

Run diagnostics without changing local state:

```powershell
python dev_tools_scripts_runner.py --doctor
```

Commit and push an explicitly requested change:

```powershell
python dev_tools_scripts_runner.py ship-main --message "type: explain the change"
```

## Rules

- Read `CLAUDE.md` before making project-wide assumptions.
- Read `AGENTS.md` when aligning behavior with Codex.
- Keep changes scoped and preserve user edits.
- Do not push unless the user explicitly requested a push in the current task,
  or the user directly invoked the `ship-main` script.
- If `ship-main` fails, report the failed step and the report path instead of
  retrying blindly.
- `ship-main` runs the quick quality gate itself, then pushes with `--no-verify`
  to avoid repeating the same pre-push gate.
