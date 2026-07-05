---
name: ci-fix
description: Use when GitHub Actions, pre-commit, pre-push, pytest, mypy, ruff, sqlfluff, Docker smoke, or Playwright checks are failing.
---

# CI Fix Workflow

Start from the exact failing command and log excerpt — do not fix based on a guess about what probably broke.

## Workflow

1. Rules are loaded via `CLAUDE.md` imports; if working as a subagent, read `AGENTS.md` (compiled ruleset).
2. Capture the failing job, command, file, line, and commit.
3. Reproduce the smallest failing command locally when possible.
4. Fix the root cause with the smallest behavior-preserving patch.
5. Run the targeted failing check.
6. Run the relevant quality gate when feasible:

```powershell
python dev_tools_scripts_runner.py --profile quick
```

## Notes

- If `gh` or GitHub connector access is unavailable, say so and continue with local reproduction.
- Prefer deterministic test fixes over loosening assertions.
- A monkeypatch that stops intercepting a call after a module split is a known project-specific failure mode (see `.ai/project/12-domain-rules.md`) — check for it before assuming a test is simply flaky.
- Do not push to `main` unless the current user turn explicitly asks for it.
- For a broader, delegated investigation, use the `country-atlas-ci-triage` agent.
