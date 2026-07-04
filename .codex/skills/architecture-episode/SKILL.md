---
name: country-atlas-architecture-episode
description: Use when implementing a planned Country Decision Atlas architecture episode from docs/_arch_.
---

# Architecture Episode Workflow

Use this workflow for planned episodes such as methodology, flows, localization,
trust, passports, or marketplace work.

## Workflow

1. Read `AGENTS.md`.
2. Read the relevant `docs/_arch_` episode and nearby invariants before editing.
3. Create or switch to a `codex/` branch for the logical unit of work.
4. Identify affected services, repositories, migrations, API schemas, contracts,
   frontend surfaces, and tests.
5. Implement with zero unrelated refactors.
6. Regenerate contracts when OpenAPI changes.
7. Run targeted tests first, then `python dev_tools_scripts_runner.py --profile quick`.
8. Review the diff for behavior changes, migration safety, and missing coverage.

## Guardrails

- Preserve default behavior unless the episode explicitly changes it.
- Keep routers thin, services domain-focused, and SQL in repositories.
- Do not add countries, languages, or AI-driven translation unless requested.
- Missing config or invariant violations should fail loudly rather than create
  a second silent source of truth.
