---
name: country-atlas-ci-fix
description: Use when GitHub Actions, pre-commit, tests, typing, lint, SQL lint, Docker smoke, or Playwright checks fail.
---

# CI Fix Workflow

Start from the exact failing command and log excerpt.

## Workflow

1. Read `AGENTS.md`.
2. Capture the failing job, command, file, line, and commit.
3. Reproduce the smallest failing command locally when possible.
4. Fix the root cause with the smallest behavior-preserving patch.
5. Run the targeted failing check.
6. Run the relevant quality gate when feasible:

```powershell
python dev_tools_scripts_runner.py --profile quick
```

## Notes

- If `gh` or GitHub connector access is unavailable, say so and continue with
  local reproduction.
- Prefer deterministic test fixes over loosening assertions.
- Do not push to `main` unless the current user turn explicitly asks for it.
