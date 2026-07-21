# Documentation

Country Decision Atlas's documentation, organized by purpose. All documentation
is written in English (the whole project is oriented toward an English-speaking
audience). This index links everything below; each document also cross-links
to the others it depends on.

Two hard rules carried over from the previous documentation structure:

- `docs/_ideas_and_concepts_/` (if present) is the owner's private folder —
  never read, edit, delete, or reference it.
- New documentation files are created only on direct request, except for
  keeping `docs/architecture` and `docs/product` accurate when the
  architecture, structure, or plan actually changes (see
  `.ai/project/10-project-map.md`).

## Architecture — what's built and how it's shaped

- [architecture/overview.md](architecture/overview.md) — the current system state, grounded in code facts: the domain map, layers, the operational surface, and a change log since the baseline.
- [architecture/layers-and-boundaries.md](architecture/layers-and-boundaries.md) — the application map, the synchronous and asynchronous request paths, and the boundaries between `apps/api`, `apps/web`, `apps/notifier`, and `apps/worker`.
- [architecture/invariants.md](architecture/invariants.md) — the binding invariants registry; breaking any entry blocks a merge regardless of a green quality gate.
- [architecture/rights-and-roles.md](architecture/rights-and-roles.md) — the roles, capability grants, visibility, and feature-flag model, plus the moderator institution and the autonomy pyramid.
- [architecture/visual-system-and-architecture-notes.md](architecture/visual-system-and-architecture-notes.md) — founding visual-system and architecture vision notes (2026-06-21), kept as the original reasoning record; see `overview.md` for what's actually built.
- [architecture/cii-methodology-notes.md](architecture/cii-methodology-notes.md) — founding CII methodology research notes (2026-06-21): the scientific basis, unique metrics, and the original rollout plan.

## API — the contract with the outside world

- [api/overview.md](api/overview.md) — REST conventions: versioning, the error envelope, authentication and RBAC, localization, idempotency, and the required order for changing the contract.

## Product — direction and plan

- [product/vision.md](product/vision.md) — what Country Decision Atlas is, its differentiation, its audience, and the product decisions locked in by the owner.
- [product/roadmap.md](product/roadmap.md) — the episode-by-episode implementation plan, current status per episode, the visual and integration tranches, and cross-cutting engineering themes.

## Decisions — the owner's decision log

- [decisions/open-questions.md](decisions/open-questions.md) — adopted owner decisions (D-1…D-12) and the questions still open (Q-1…Q-3), each dated.

## Operations — how work gets done

- [operations/working-standard.md](operations/working-standard.md) — the unified working standard: git workflow, the quality gate, layer implementation order, hard prohibitions, and the final-report format.
- [operations/synthetic-data-plan.md](operations/synthetic-data-plan.md) — the synthetic-data pipeline's master plan and stage-by-stage status (stages 0–2 implemented; 3–4 pending).

## Research — market and domain research behind the product

- [research/market/00-index.md](research/market/00-index.md) — an index and summary of the market-research package (market size, competitors, monetization, positioning).
- [research/market/01-market-overview.md](research/market/01-market-overview.md) through [05-product-opportunity-and-positioning.md](research/market/05-product-opportunity-and-positioning.md) — the full 5-file market package.
- [research/migration/00-overview-and-sources.md](research/migration/00-overview-and-sources.md) — a 120-question migration research overview, methodology, personas, and a 50-source bibliography.
- [research/migration/01-migration-dynamics-and-intent.md](research/migration/01-migration-dynamics-and-intent.md) through [05-challenges-demand-and-future-trends.md](research/migration/05-challenges-demand-and-future-trends.md) — the full 6-file migration research package.
- [research/mobility-trends/overview.md](research/mobility-trends/overview.md) — global mobility market statistics and strategic positioning, overlapping with `research/migration/` but focused on market sizing.
- [research/deep-dive/product-insights-and-data-model.md](research/deep-dive/product-insights-and-data-model.md) — the object data model, the Country Direction/Drift Index's original design, and the MVP-readiness decision.
- [research/competitive-analysis/review-platforms-and-takeaways.md](research/competitive-analysis/review-platforms-and-takeaways.md) — a Quora/Trustpilot/Glassdoor pattern analysis.
- [research/competitive-analysis/feature-matrix-50-competitors.csv](research/competitive-analysis/feature-matrix-50-competitors.csv) — a structured feature matrix across 50 adjacent products.

## Elsewhere in the repository

- `.ai/universal/` and `.ai/project/` — the rule modules that govern how AI assistants work in this repo (branching, the quality gate, architecture boundaries, domain rules).
- `utils/synthetic_data/README.md` — the synthetic-data pipeline in full implementation detail (this folder's `operations/synthetic-data-plan.md` is the plan; that README is the as-built reference).
- The root [README.md](../README.md) — project setup, the tech stack, and quick-start instructions.
