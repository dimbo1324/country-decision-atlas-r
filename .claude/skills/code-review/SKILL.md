---
name: code-review
description: Use for reviewing Country Decision Atlas diffs, branches, pull requests, or uncommitted changes.
---

# Code Review Workflow

Review like an owner. Findings come first.

## Focus

- Correctness and behavior regressions.
- Security, privacy, and data-quality risks.
- Migration safety and idempotency (never touch an already-applied migration file).
- Contract drift between FastAPI, OpenAPI, generated types, and frontend usage.
- Missing or weak tests, including monkeypatch targets broken by a module split.
- Flaky Playwright or runtime smoke assumptions.

## Output

Return findings ordered by severity with file and line references where possible. Keep the summary short and secondary. If no issues are found, say so clearly and mention residual risk or test gaps.

For a larger or higher-stakes diff, delegate to the `country-atlas-quality-reviewer` agent instead of reviewing inline — it runs in a fresh context and won't be anchored on the reasoning that produced the change.
 