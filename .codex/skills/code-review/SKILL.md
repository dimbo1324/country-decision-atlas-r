---
name: country-atlas-code-review
description: Use for reviewing Country Decision Atlas diffs, branches, pull requests, or uncommitted changes.
---

# Code Review Workflow

Review like an owner. Findings come first.

## Focus

- Correctness and behavior regressions.
- Security, privacy, and data-quality risks.
- Migration safety and idempotency.
- Contract drift between FastAPI, OpenAPI, generated types, and frontend usage.
- Missing or weak tests.
- Flaky Playwright or runtime smoke assumptions.

## Output

Return findings ordered by severity with file and line references where
possible. Keep the summary short and secondary. If no issues are found, say so
clearly and mention residual risk or test gaps.
