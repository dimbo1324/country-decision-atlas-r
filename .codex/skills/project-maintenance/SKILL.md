---
name: country-atlas-project-maintenance
description: Use for Country Decision Atlas maintenance: formatting, quick/full quality gates, assistant docs, commits, and explicitly requested main pushes.
---

# Country Atlas Project Maintenance

Use repository automation before hand-written command sequences.

## Fast Paths

Format all supported code:

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

Regenerate the Codex entry after editing rule modules in `.ai/`:

```powershell
python dev_tools_scripts_runner.py sync-agents
```

## Rules

- `AGENTS.md` is GENERATED from `.ai/` modules — never hand-edit it; edit the
  module and run `sync-agents`. `CLAUDE.md` imports the same modules natively.
- Preserve user changes and never revert unrelated work.
- Do not push unless the user explicitly requested a push in the current task
  or directly invoked `ship-main`.
- If `ship-main` fails, report the failed step and report path instead of
  retrying blindly.
