---
name: country-atlas-architecture-episode
description: Use when implementing a planned Country Decision Atlas architecture episode from docs/product/roadmap.md.
---

# Architecture Episode Workflow

Use this workflow for planned episodes such as methodology, flows, localization,
trust, passports, or marketplace work.

## Workflow

1. Run the orientation ritual from `.ai/project/13-progress-tracking.md`: git
   state, episode statuses in the plan, previous `task-checklist.md`.
2. Read the relevant `docs/product/roadmap.md` episode description and the
   invariants registry (`docs/architecture/invariants.md`) before editing.
   Files are the source of truth, not memory of a prior session.
3. Create a feature branch (`feat/<episode-slug>`) from up-to-date `main`.
4. Write `task-checklist.md` for the episode per
   `.ai/universal/02-task-checklist.md`; commit and push it before
   implementation.
5. Identify affected services, repositories, migrations, API schemas,
   contracts, frontend surfaces, and tests.
6. Implement with zero unrelated refactors.
7. Regenerate contracts when OpenAPI changes.
8. Run targeted tests first, then the full gate before merge
   (`python dev_tools_scripts_runner.py`).
9. Review the diff for behavior changes, migration safety, and missing
   coverage.
10. Mark the episode's `**Статус.**` line in `01_План_реализации.md`, fill the
    task checklist with `+`/`-`, and write the final report.

## Guardrails

- Preserve default behavior unless the episode explicitly changes it.
- Keep routers thin, services domain-focused, and SQL in repositories.
- Do not add countries, languages, or AI-driven translation unless requested.
- Missing config or invariant violations should fail loudly rather than create
  a second silent source of truth.
