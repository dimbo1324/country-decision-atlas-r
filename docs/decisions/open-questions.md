# Owner Decisions and Open Questions

> A log of the owner's product decisions and the questions still outstanding. Adopted decisions have been folded into the relevant documents (vision, the roadmap, the invariants registry) — this file records the original decision with its date.

---

## 1. Decisions made (2026-07-04)

| # | Topic | Decision |
|---|---|---|
| D-1 | Test countries (RU/UY/AR) | **Never deleted.** Until Episode 5 — a working test set. After Episode 5 — hidden from public surfaces and preserved as a **restorable demo set**: exported to fixtures (a JSON dump) + a dev tool for fast restoration under `scripts/dev_tools/` (registered in the orchestrator). Detail: the roadmap, Episode 5 |
| D-2 | Moderating author methodologies | Premoderation until roughly the first 50 authors; the threshold for switching to postmoderation is a rejection rate that stays stably under 10% |
| D-3 | Monetization | Operating jurisdiction — **Uruguay**. The model is set: (a) voluntary donations to the platform with no privileges + (b) donations to authors with a platform fee. Timing is undefined (not a blocker). Provider candidates to research during the integration tranche: dLocal (Montevideo), Mercado Pago, PayPal |
| D-4 | Contribution license | Option (c): country data carries a non-exclusive, perpetual license to the platform; author methodologies get the author's choice at publish time (a platform license \| CC BY-SA) |
| D-5 | ~~The `research/03–07` folders~~ (superseded 2026-07-21, see below) | ~~Kept as is, structure untouched~~ |
| D-6 | An email channel | Backlog; the early audience is covered by Telegram |
| D-7 | Metric names | A naming revision during the visual tranche; the style — **evocative** |
| D-8 | Locale in the URL | Adopted: locale-in-URL for public pages; the scheme was finalized before the visual tranche |
| D-9 | `CHANGELOG.json` | Not restored; task history lives in git + final reports |
| D-10 | The autonomous-development period | Until the owner's relocation to Uruguay (~3–4 months from 2026-07): **no real external connections** (the LLM API, a live Telegram bot, email, payments, OAuth). Episodes 1–7 are all built and tested fully offline through fake seams; real connections come in a separate "integration tranche" after the move. Wherever a connection will eventually be needed, a seam is built now |
| D-11 | E2E/smoke fixtures vs. the demo set (audit finding P1-9, hardening audit episode 8) | **Option B (interim), option A once E2E moves onto the synthetic pipeline.** For now: `--visible` still temporarily lifts `is_demo` only in CI/dev jobs, and it's confirmed and tested that the script's default path never disturbs the demo set. `utils/synthetic_data/` (entry point `scripts/synthetic_data.py`, moved from `scripts/synthetic_data`/`docs/synthetic_data` — see [../operations/synthetic-data-plan.md](../operations/synthetic-data-plan.md), Stage 0) has reached Stage 7 (dataset-isolated `dataset_id` fixtures and quality-gate integration are implemented), but actually switching E2E/smokes onto the synthetic set and removing `--visible` from CI is a separate, not-yet-started task (see [../operations/synthetic-data-plan.md](../operations/synthetic-data-plan.md), Stage 3). Detail: the roadmap, Episode 8; `utils/synthetic_data/README.md` |
| D-12 | The i18n strategy for the redesign's UI content (recorded 2026-07-18, Stage 5 "Lock-in"; **SUPERSEDED 2026-07-19**, see below) | ~~**Interface labels stay Russian-only; `next-intl` remains only for the app's "chrome."**~~ Not a new owner decision, but an explicit acknowledgment of a pattern that had already emerged de facto across every redesign wave (stages 0-3) and follows directly from the existing rule in `.ai/project/12-domain-rules.md` ("don't use AI translation without the owner's explicit request"). Verified against the code: the `next-intl` message catalog (`apps/web/src/messages/{en,ru}.json`, 90 keys) only covered the header/footer/auth forms/the search palette/error pages — not a single key for feature or page content. Every label added during the redesign (dossier tab names, the matching-wizard's steps, filter-chip labels, catalog captions) was hardcoded as a Russian string, independent of the `/en/` vs. `/ru/` URL locale. **The owner revisited this decision on 2026-07-19** (task `feat/i18n-three-language-interface`, its `task-checklist.md`): a full end-to-end interface migration to three languages — English (the new default locale, previously Russian), Russian, Spanish — was completed across all 154 files on the public surface (`apps/web/src/app/[locale]/**` and the feature components rendered on them), 10 stages, growing the message catalog from 90 to 1023 keys per locale (`i18n_parity_check.py`, a 3-locale parity check). The scope is still limited to the **interface** (chrome + labels, navigation, forms, tab/step names) — the backend's content data (country names, scenario names, source text, legal-signal bodies, methodology text) stays in its original language regardless of interface locale; for the `es` locale it's requested from the backend with a fallback to `en` via the new `toApiLocale()` (the backend's `LocaleCode` contract is still only `en`\|`ru`; Spanish isn't planned at the data layer). `/internal/**` (the admin/moderation console) is out of scope, untouched. A full description of the boundary, the bugs found and fixed along the way, and the remaining tech debt (a missing `ariaLabel` on `packages/ui`'s `Breadcrumbs` on 4 already-migrated pages; a `Negative`/`Adverse` mismatch between two different label sources for the same enum value) — see `task-checklist.md` at the repo root. |

## 2. Still-open questions

### Q-1. The first moderators

**Status:** the owner is unsure yet (2026-07-04). **What's needed:** the phase-1 moderator headcount and whether candidates exist; confirming/adjusting admission thresholds (reputation, tenure). **Blocks:** phase 1 of the moderator institution — the mechanism itself (Episode 3) ships independently; the question becomes relevant once the author surface launches (Episode 4, invite-only authors). Until then, the owner handles moderation themselves.

### Q-2. Hosting and production deployment

**Status:** the owner is unsure yet (2026-07-04). **What's needed:** a venue (VPS/cloud), a region, a budget; the standing recommendation is that a single host with docker-compose is enough at launch. **Blocks:** the public launch of Episode 2 (reminders need an always-on host). Doesn't block development: fake-mode delivery is fully testable locally. The natural decision point is the integration tranche; for Uruguay, factor in latency to the audience (an EU or US-East region is probably enough).

### Q-3. Monetization timing

**Status:** undefined (2026-07-04), deliberately. **Blocker:** none — the foundation (D-3, D-4, the safeguards in the invariants registry §6) is being laid independently of timing.

---

## Note (2026-07-21)

D-5 above (the `03–07` research folders staying untouched) was superseded by
a direct, explicit owner instruction on 2026-07-21 to reorganize the entire
former `docs/_arch_` tree — including those research folders — into the
current `docs/` structure (`research/market/`, `research/migration/`,
`research/mobility-trends/`, `research/deep-dive/`,
`research/competitive-analysis/`) and to translate all documentation into
English, since a later, explicit instruction in the current conversation
overrides an earlier recorded decision (see `CLAUDE.md`: "an explicit owner
instruction in the current conversation overrides everything"). The content
of the research documents was preserved; only their location, filenames, and
language changed.
