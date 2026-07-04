---
name: architecture-episode
description: Use when implementing a planned Country Decision Atlas architecture episode from docs/_arch_/02_План/01_План_реализации.md.
---

# Architecture Episode Workflow

Use this workflow for planned episodes such as flexible methodology, trip planner, rights/capabilities, author metrics, country contribution, migration flows, or contact threads.

## Workflow

1. Read `CLAUDE.md`.
2. Read the relevant `docs/_arch_` episode description and the invariants registry (`docs/_arch_/02_План/02_Реестр_инвариантов.md`) before editing anything. Plans and invariants can change between sessions — treat the files as the source of truth, not memory of a prior conversation.
3. Create or switch to a feature branch for the logical unit of work.
4. Identify affected services, repositories, migrations, API schemas, contracts, frontend surfaces, and tests. For non-trivial scope, delegate this step to `country-atlas-domain-architect` rather than guessing.
5. Implement with zero unrelated refactors — an episode is not an invitation to also clean up nearby code.
6. Regenerate contracts (`pnpm contracts:generate`) when the OpenAPI schema changes.
7. Run targeted tests first, then `python dev_tools_scripts_runner.py --profile quick`.
8. Review the diff for behavior changes, migration safety, and missing coverage before calling the episode done — use `country-atlas-quality-reviewer` for a second pass on anything security- or data-quality-sensitive.

## Guardrails

- Preserve default behavior unless the episode explicitly changes it (most episodes are additive layers over locked core math — see the invariants registry).
- Keep routers thin, services domain-focused, and SQL in repositories.
- Do not add countries, languages, or AI-driven translation unless the user explicitly asked.
- Missing config or an invariant violation should fail loudly rather than create a second silent source of truth.
- Remember the project's autonomous-development-mode invariant: no real external service goes live before the integration tranche. New integrations land behind a fake-by-default provider seam.
